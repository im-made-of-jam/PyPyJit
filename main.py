# this flat out does not support threading due to the way variables are handled
# the stack is purely used as a call stack

import Compilator.Parser.Line

import Compilator.Processing.Combinator

import Compilator.Codegen.CodeFromToken

fileLines = []
fileTokens = []
declaredNames = []

with open("test.pyj") as openFile:
    fileLines = openFile.readlines()

    fileLines = [line.strip() for line in fileLines]

for count, line in enumerate(fileLines):
    if line == "":
        continue

    fileTokens.append(Compilator.Processing.Combinator.combineIfPossibleStage1(Compilator.Parser.Line.tokeniseLine(line, count)))

stage2 = Compilator.Processing.Combinator.combineIfPossibleStage2(fileTokens)

def printToken(tk, indent=0):
    for _ in range(indent):
        print("    ", end="")

    print(tk)

    if len(tk.subTokens):
        for stk in tk.subTokens:
            printToken(stk, indent + 1)

for tk in stage2:
    printToken(tk)
