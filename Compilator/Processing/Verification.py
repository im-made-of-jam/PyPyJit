from ..Parser.Token import *

def VerifyLabels(tokenList: list[Token | InternalToken]) -> bool:
    # checks that all call statements have the name of either an import or a function declaration
    # also checks that goto statements have a valid label as their jump target

    labelsList = []
    functionList = []

    # first pass to fetch all labels
    for tk in tokenList:
        if isinstance(tk, LabelKeyword):
            if tk.stringContent in labelsList:
                print(f"duplicate label definition with name: {tk.stringContent} on line {tk.originalSourceLine}")
                return False

            labelsList.append(tk.stringContent)

        if isinstance(tk, DeclaringFunction):
            if tk.stringContent in functionList:
                print(f"duplicate function definition with name: {tk.stringContent} on line {tk.originalSourceLine}")
                return False

            functionList.append(tk.stringContent)

        if isinstance(tk, DeclaringImport):
            if tk.stringContent in functionList:
                print(f"duplicate function definition with name: {tk.stringContent} on line {tk.originalSourceLine}")
                return False

            functionList.append(tk.stringContent)

    # now have a list of all function names and label names
    # so go through it all again to ensure jump targets area valid
    for tk in tokenList:
        if isinstance(tk, JumpStatement):
            if tk.stringContent not in labelsList:
                print(f"invalid jump target with name: {tk.stringContent} on line {tk.originalSourceLine}")
                return False

        if isinstance(tk, CallStatement):
            if tk.stringContent not in functionList:
                print(f"invalid call target with name: {tk.stringContent} on line {tk.originalSourceLine}")
                return False

    return True
