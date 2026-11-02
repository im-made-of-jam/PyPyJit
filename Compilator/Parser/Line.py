from .Token import *
from .Keywords import *

def tokeniseLine(line: str) -> list[Token]:
    line = line.strip()

    splitLine = line.split()

    tokenList = []

    for word in splitLine:
        tokenList.append(getTokenFromWord(word))

    return tokenList
