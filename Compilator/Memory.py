import ctypes
from ctypes import wintypes
import sys

allocationSize = 4096
nullptr = ctypes.c_void_p(None)

# allocation constants
MEM_COMMIT      = 0x00001000
MEM_RESERVE     = 0x00002000
MEM_RESET       = 0x00080000
MEM_RESET_UNDO  = 0x01000000

MEM_LARGE_PAGES = 0x20000000
MEM_PHYSICAL    = 0x00400000
MEM_TOP_DOWN    = 0x00100000
MEM_WRITE_WATCH = 0x00200000

MEM_DECOMMIT    = 0x00004000
MEM_RELEASE     = 0x00008000
MEM_COALESCE_PLACEHOLDERS = 0x00000001
MEM_PRESERVE_PLACEHOLDER  = 0x00000002

# memory protection constants
PAGE_EXECUTE                = 0x10
PAGE_EXECUTE_READ           = 0x20
PAGE_EXECUTE_READWRITE      = 0x40
PAGE_EXECUTE_WRITECOPY      = 0x80

PAGE_NOACCESS               = 0x01
PAGE_READONLY               = 0x02
PAGE_READWRITE              = 0x04
PAGE_WRITECOPY              = 0x08

PAGE_TARGETS_INVALID        = 0x40000000
PAGE_TARGETS_NO_UPDATE      = 0x40000000

PAGE_GUARD                  = 0x100
PAGE_NOCACHE                = 0x200
PAGE_WRITECOMBINE           = 0x400

PAGE_ENCLAVE_DECOMMIT       = 0x10000000
PAGE_ENCLAVE_THREAD_CONTROL = 0x80000000
PAGE_ENCLAVE_UNVALIDATED    = 0x20000000

kernel32 = ctypes.windll.LoadLibrary("kernel32.dll")
_VirtualAlloc = kernel32.VirtualAlloc
_VirtualAlloc.restype = ctypes.c_void_p

# python wrapper for kernel32.VirtualAlloc
def VirtualAlloc(lpAddress: int, dwSize: int, flAllocationType: int, flProtect: int) -> ctypes.c_void_p:
    kernel32.VirtualAlloc.restype = ctypes.c_void_p
    return ctypes.c_void_p(kernel32.VirtualAlloc(ctypes.c_void_p(lpAddress),
                                                 ctypes.c_size_t(dwSize),
                                                 wintypes.DWORD(flAllocationType),
                                                 wintypes.DWORD(flProtect)))

# python wrapper foro kernel32.VirtualFree
def VirtualFree(lpAddress: ctypes.c_void_p, dwSize: int, dwFreeType: int) -> int:
    return ctypes.windll.kernel32.VirtualFree(lpAddress, wintypes.DWORD(dwSize), wintypes.DWORD(dwFreeType))

# python wrapper for kernel32.VirtualQuery
def VirtualQuery(lpaddress: ctypes.c_void_p, lpBuffer: ctypes.c_void_p, dwLength: ctypes.c_size_t):
    return ctypes.c_void_p(kernel32.VirtualQuery(lpaddress, lpBuffer, dwLength))

# python wrapper for kernel32.VirtualProtect
def VirtualProtect(lpAddress: ctypes.c_void_p, dwSize: ctypes.c_size_t, flNewProtect: int) -> int:
    intIDontCareAbout = wintypes.DWORD(0)
    return ctypes.c_bool(kernel32.VirtualProtect(lpAddress, dwSize, wintypes.DWORD(flNewProtect), ctypes.pointer(intIDontCareAbout))).value

# python wrapper for kernel32.FlushInstructionCache
def FlushInstructionCache(hProcess: wintypes.HANDLE, lpBaseAddress: ctypes.c_void_p, dwSize: ctypes.c_size_t) -> int:
    return ctypes.c_bool(kernel32.FlushInstructionCache(hProcess, lpBaseAddress, dwSize)).value

# python wrapper for kernel32.GetCurrentProcess
def GetCurrentProcess() -> int:
    return kernel32.GetCurrentProcess()

# writes a qword at a given address. expects big endian, will convert automatically
def _writeQWordAt(address: ctypes.c_void_p, value: int) -> None:
    bytePointer = ctypes.cast(valueOfPointer(address), ctypes.POINTER(ctypes.c_uint64))
    bytePointer[0] = ctypes.c_uint64(fixQwordEndianness(value))

# reads a qword at a given address. returns as if the number was big endian
def _readQWordAt(address: ctypes.c_void_p) -> int:
    bytePointer = ctypes.cast(valueOfPointer(address), ctypes.POINTER(ctypes.c_uint64))
    return fixQwordEndianness(bytePointer.contents.value)


# reads a byte from a specific address
def _readByteFrom(address: ctypes.c_void_p) -> int:
    bytePointer = ctypes.cast(address, ctypes.POINTER(ctypes.c_uint8))
    return bytePointer.contents.value

def _getMemoryProtection(allocationBase: ctypes.c_void_p) -> int:
    class MEMORY_BASIC_INFORMATION(ctypes.Structure):
        # see windows documentation
        _fields_ = [
                ("BaseAddress",       ctypes.c_void_p),
                ("AllocationBase",    ctypes.c_void_p),
                ("AllocationProtect", wintypes.DWORD),
                ("PartitionId",       wintypes.WORD),
                ("RegionSize",        ctypes.c_size_t),
                ("State",             wintypes.DWORD),
                ("Protect",           wintypes.DWORD),
                ("Type",              wintypes.DWORD)
        ]

    memoryBasicInformation = MEMORY_BASIC_INFORMATION()

    vqResult = VirtualQuery(allocationBase,
                              ctypes.cast(ctypes.pointer(memoryBasicInformation), ctypes.c_void_p),
                              ctypes.c_size_t(ctypes.sizeof(MEMORY_BASIC_INFORMATION))
                             )

    return memoryBasicInformation.Protect

def _setMemoryProtection(allocationBase: ctypes.c_void_p, newProtection: int) -> int:
    rv = VirtualProtect(allocationBase, ctypes.c_size_t(allocationSize), newProtection)
    rv2 = FlushInstructionCache(ctypes.c_void_p(GetCurrentProcess()), nullptr, ctypes.c_size_t(0))

    return 1 if rv and rv2 else 0

# gets the address of a pointer as an int
# e.g. (void*)(0x0A0A0A0A) -> 0x0A0A0A0A
def valueOfPointer(pointer: ctypes.c_void_p) -> int:
    if pointer.value is None:
        return 0

    return pointer.value

def jumpTo(pointer: int) -> None:
    function = ctypes.WINFUNCTYPE(None)(pointer)
    function.restype = None
    function()

# makes a python int have the correct system endianness
def fixQwordEndianness(qword: int) -> int:
    return int.from_bytes(qword.to_bytes(8, "big"), sys.byteorder)

class SlotPageTracker:
    def __init__(self, baseAddress=0):
        self.useList = [False] * (allocationSize // 8)
        self.baseAddress = 0

    def __del__(self):
        VirtualFree(ctypes.c_void_p(self.baseAddress), 0, MEM_DECOMMIT | MEM_RELEASE)

class CodePageTracker:
    def __init__(self, baseAddress=0):
        self.usedBytes = 0
        self.baseAddress = 0

    def __del__(self):
        VirtualFree(ctypes.c_void_p(self.baseAddress), 0, MEM_DECOMMIT | MEM_RELEASE)

if __name__ == "__main__":
    lpAllocatedAddress = VirtualAlloc(0, allocationSize, MEM_COMMIT | MEM_RESERVE | MEM_TOP_DOWN, PAGE_READWRITE)

    print(f"allocated at: {hex(valueOfPointer(lpAllocatedAddress))}")

    print(_setMemoryProtection(lpAllocatedAddress, PAGE_EXECUTE_READWRITE))
    print(f"Memory Protection: {_getMemoryProtection(lpAllocatedAddress)}")

    _writeQWordAt(lpAllocatedAddress, 0xB000480FBEC0C3C3)

    ourFunction = ctypes.WINFUNCTYPE(None)(valueOfPointer(lpAllocatedAddress))
    ourFunction.restype = ctypes.c_uint64
    print(ourFunction())

    print(_getMemoryProtection(lpAllocatedAddress))

    VirtualFree(lpAllocatedAddress, 0, MEM_RELEASE)
