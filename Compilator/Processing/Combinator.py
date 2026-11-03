from ..Parser.Token import *

# combines one line of tokens into other tokens
# larger things such as blocks for functions are handled in later stages
def combineIfPossibleStage1(tokenList: list[Token]) -> Token | InternalToken:
    if len(tokenList) != 0:
        if isinstance(tokenList[0], CallKeyword):
            # call statement and function declarations are the only sattements with variable arguments at present
            if len(tokenList) < 2:
                print(f"call statement without a function name {tokenList[0].originalSourceLine}: [{tokenList}]")
                return InternalErrorToken("call statement without a function name", originalSourceLine=tokenList[0].originalSourceLine)

            return CallStatement(tokenList[1].stringContent, tokenList[2:], originalSourceLine=tokenList[0].originalSourceLine)

        elif isinstance(tokenList[0], FunctionKeyword):
            if len(tokenList) < 2:
                print(f"function declaration without a name {tokenList[0].originalSourceLine}: [{tokenList}]")
                return InternalErrorToken("function declaration without a name", originalSourceLine=tokenList[0].originalSourceLine)

            return DeclaringFunction(tokenList[1].stringContent, tokenList[2:], originalSourceLine=tokenList[0].originalSourceLine)

    if len(tokenList) == 1:
        # ideally just single character tokens
        return tokenList[0]

    elif len(tokenList) == 2:
        # if with variable
        if isinstance(tokenList[0], IfKeyword):
            return IfSingleStatement(tokenList[1].stringContent, originalSourceLine=tokenList[0].originalSourceLine)

        # declarations
        if isinstance(tokenList[0], IntegerKeyword):
            return DeclaringInteger(tokenList[1].stringContent, originalSourceLine=tokenList[0].originalSourceLine)

        if isinstance(tokenList[0], FloatKeyword):
            return DeclaringFloat(tokenList[1].stringContent, originalSourceLine=tokenList[0].originalSourceLine)

        if isinstance(tokenList[0], ImportKeyword):
            return DeclaringImport(tokenList[1].stringContent, originalSourceLine=tokenList[0].originalSourceLine)

        if isinstance(tokenList[0], LabelKeyword):
            return DeclaringLabel(tokenList[1].stringContent, originalSourceLine=tokenList[0].originalSourceLine)

        # jump and call
        if isinstance(tokenList[0], GotoKeyword):
            return JumpStatement(tokenList[1].stringContent, originalSourceLine=tokenList[0].originalSourceLine)

    elif len(tokenList) == 3:
        if isinstance(tokenList[0], AnythingElse):
            # left side is something that isnt a keyword
            if isinstance(tokenList[1], EqualsSymbol):
                # we are assigning something to something in here
                if isinstance(tokenList[2], IntegerLiteral):
                    return AssigningInteger(tokenList[2].stringContent, [tokenList[0]], originalSourceLine=tokenList[0].originalSourceLine)

                if isinstance(tokenList[2], FloatLiteral):
                    return AssigningFloat(tokenList[2].stringContent, [tokenList[0]], originalSourceLine=tokenList[0].originalSourceLine)

                if isinstance(tokenList[2], AnythingElse):
                    return AssigningVariableToVariable(subTokens=[tokenList[0], tokenList[2]], originalSourceLine=tokenList[0].originalSourceLine)

            if isinstance(tokenList[1], AddSymbol):
                return AdditionStatement(subTokens=[tokenList[0], tokenList[2]], originalSourceLine=tokenList[0].originalSourceLine)

            if isinstance(tokenList[1], MinusSymbol):
                return MinusStatement(subTokens=[tokenList[0], tokenList[2]], originalSourceLine=tokenList[0].originalSourceLine)

            if isinstance(tokenList[1], MultiplySymbol):
                return MultiplyStatement(subTokens=[tokenList[0], tokenList[2]], originalSourceLine=tokenList[0].originalSourceLine)

            if isinstance(tokenList[1], DivideSymbol):
                return DivideStatement(subTokens=[tokenList[0], tokenList[2]], originalSourceLine=tokenList[0].originalSourceLine)

            if isinstance(tokenList[1], ModuloSymbol):
                return ModuloStatement(subTokens=[tokenList[0], tokenList[2]], originalSourceLine=tokenList[0].originalSourceLine)

            if isinstance(tokenList[1], BitwiseNotSymbol):
                return UnaryNotStatement(subTokens=[tokenList[0], tokenList[2]], originalSourceLine=tokenList[0].originalSourceLine)

    elif len(tokenList) == 4:
        # if with comparison
        if isinstance(tokenList[0], IfKeyword):
            if isinstance(tokenList[2], IsKeyword):
                return IfEqualityStatement(subTokens=[tokenList[1], tokenList[3]], originalSourceLine=tokenList[0].originalSourceLine)

            if isinstance(tokenList[2], LessThanSymbol):
                return IfLessThanStatement(subTokens=[tokenList[1], tokenList[3]], originalSourceLine=tokenList[0].originalSourceLine)

            if isinstance(tokenList[2], GreaterThanSymbol):
                return IfGreaterThanStatement(subTokens=[tokenList[1], tokenList[3]], originalSourceLine=tokenList[0].originalSourceLine)

    somethingElseString = ""

    for tk in tokenList:
        somethingElseString += tk.stringContent

    return SomethingElseInternal(somethingElseString, originalSourceLine=tokenList[0].originalSourceLine)

# this takes a list of tokens that have come from stage 1, and finds blocks to combine into one token with sub tokens
def combineIfPossibleStage2(tokenList: list[Token | InternalToken]) -> list[Token | InternalToken]:
    # this could be element zero but its separate so we have something to return if this function gets messed up
    globalTokenScope: list[Token | InternalToken] = []

    # stack of opening curlies so we know which block we are currently in
    blockStack: list[BlockExpression] = []

    # go through every single token
    for tk in tokenList:
        if isinstance(tk, OpenCurlySymbol):
            # keep track of where this new block is, but dont add it to its parent block yet, we do that when it closes
            blockStack.append(BlockExpression())
            # keep track of line number as start of block
            blockStack[-1].originalSourceLine = tk.originalSourceLine

        elif isinstance(tk, ClosingCurlySymbol):
            # now we add it to its parent block
            if len(blockStack) >= 2:
                # parent block is another block
                poppedBlock = blockStack.pop()
                blockStack[-1].subTokens.append(poppedBlock)

            elif len(blockStack) == 1:
                # parent block is global scope
                globalTokenScope.append(blockStack.pop())

            else:
                # no opening curly to match this closing curly, this is not good, so error token
                print(f"unmatched closing curly {tk.originalSourceLine}: [{tk}]")
                globalTokenScope.append(InternalErrorToken("unmatched closing curly", originalSourceLine=tk.originalSourceLine))

        else:
            # not a curly, add to relevant list
            if len(blockStack):
                blockStack[-1].subTokens.append(tk)

            else:
                globalTokenScope.append(tk)

    return globalTokenScope

# this takes the output of stage 2 and attempts to combine ifs and whiles with a block to turn them into a single token
def combineIfPossibleStage3(tokenList: list[Token | InternalToken], topLevel=True) -> list[Token | InternalToken]:
    # need at least two tokens for this stage to be able to do anything
    if len(tokenList) < 2:
        return list(tokenList)

    for i in range(len(tokenList) - 1):
        searchPair = (tokenList[i], tokenList[i + 1])

        print(searchPair)
