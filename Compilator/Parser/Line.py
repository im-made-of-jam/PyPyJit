from .Token import *
from .Keywords import *

def tokeniseLine(line: str, number: int) -> list[Token]:
    line = line.strip()

    splitLine = line.split()

    tokenList = []

    for word in splitLine:
        tokenList.append(getTokenFromWord(word))

    return tokenList
