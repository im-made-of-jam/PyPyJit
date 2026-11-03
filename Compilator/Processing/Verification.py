from ..Parser.Token import *

def verifyLabels(tokenList: list[Token | InternalToken], labelsList=[], functionList=[]) -> bool:
    # checks that all call statements have the name of either an import or a function declaration
    # also checks that goto statements have a valid label as their jump target

    # first pass to fetch all labels
    def collectLabels(tkList, lblList=labelsList, fnList=functionList):
        for tk in tkList:
            if isinstance(tk, DeclaringLabel):
                if tk.stringContent in lblList:
                    print(f"duplicate label definition with name: {tk.stringContent} on line {tk.originalSourceLine}")
                    return False

                lblList.append(tk.stringContent)

            if isinstance(tk, DeclaringFunction):
                if tk.stringContent in fnList:
                    print(f"duplicate function definition with name: {tk.stringContent} on line {tk.originalSourceLine}")
                    return False

                fnList.append(tk.stringContent)

            if isinstance(tk, DeclaringImport):
                if tk.stringContent in fnList:
                    print(f"duplicate function definition with name: {tk.stringContent} on line {tk.originalSourceLine}")
                    return False

                fnList.append(tk.stringContent)

            if len(tk.subTokens):
                collectLabels(tk.subTokens, lblList, fnList)

    collectLabels(tokenList)

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
