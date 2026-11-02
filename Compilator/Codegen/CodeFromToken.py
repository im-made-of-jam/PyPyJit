from ..Parser.Token import *
from ..Memory import VirtualAlloc, VirtualFree, VirtualProtect, VirtualQuery
from ..Memory import SlotPageTracker, CodePageTracker, allocationSize, valueOfPointer
from ..Memory import MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE, PAGE_EXECUTE_READWRITE

# each of these should be at least eight bytes for the sake of easy alignment at the moment
variableMemoryLocations: dict[str, int] = {}

# pages used for 8 byte memory slots, for varaiables and labels
_allocatedSlotPages: list[SlotPageTracker] = []

# pages used for code chunks
_allocatedCodePages: list[CodePageTracker] = []

def getNewMemorySlot() -> int:
    # get a new 8 byte memory location for a label or variable
    for page in _allocatedSlotPages:
        for slot in range(len(page.useList)):
            if not page.useList[slot]:
                page.useList[slot] = True
                return page.baseAddress + (slot * 8)

    # need a new page if we get here
    newPage = valueOfPointer(VirtualAlloc(0, allocationSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE))

    _allocatedSlotPages.append(SlotPageTracker(newPage))

    _allocatedSlotPages[-1].useList[0] = True

    return newPage

def getNewSlotLocation(name: str) -> int:
    # get a new slot for a variable
    if name not in variableMemoryLocations:
        variableMemoryLocations[name] = getNewMemorySlot()

    return variableMemoryLocations[name]

def getNewCodeSlotBase(bytesNeeded: int) -> int:
    # code may not straddle pages at the moment
    # this effectively limits function size to page size at the moment
    if bytesNeeded > allocationSize:
        return 0

    # find a slot in a code page where the code page has at least as many bytes as needed available
    # otherwise allocate a new page for the code
    for page in _allocatedCodePages:
        if (page.usedBytes + bytesNeeded) < allocationSize:
            baseAddress = page.baseAddress + page.usedBytes
            page.usedBytes += bytesNeeded

            return baseAddress

    # if we get here then we need a new page
    newPage = valueOfPointer(VirtualAlloc(0, allocationSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE))

    _allocatedCodePages.append(CodePageTracker(newPage))

    _allocatedCodePages[-1].usedBytes += bytesNeeded
    return newPage
