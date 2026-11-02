from ..Parser.Token import *

# combines one line of tokens into other tokens
# larger things such as blocks for functions are handled in later stages
def combineIfPossibleStage1(tokenList: list[Token]) -> Token | InternalToken:
    if len(tokenList) != 0:
        if isinstance(tokenList[0], CallKeyword):
            # call statement and function declarations are the only sattements with variable arguments at present
            if len(tokenList) < 2:
                return InternalErrorToken("call statement without a function name")

            argString = ""

            for tk in tokenList[2:]:
                argString += tk.stringContent
                argString += " "

            return CallStatement(argString, [tokenList[1]])

        elif isinstance(tokenList[0], FunctionKeyword):
            if len(tokenList) < 2:
                return InternalErrorToken("function declaration without a name")

            argString = ""

            for tk in tokenList[2:]:
                argString += tk.stringContent
                argString += " "

            return DeclaringFunction(argString, [tokenList[1]])

    if len(tokenList) == 1:
        # ideally just single character tokens
        return tokenList[0]

    elif len(tokenList) == 2:
        # if with variable
        if isinstance(tokenList[0], IfKeyword):
            return IfSingleStatement(tokenList[1].stringContent)

        # declarations
        if isinstance(tokenList[0], IntegerKeyword):
            return DeclaringInteger(tokenList[1].stringContent)

        if isinstance(tokenList[0], FloatKeyword):
            return DeclaringFloat(tokenList[1].stringContent)

        if isinstance(tokenList[0], ImportKeyword):
            return DeclaringImport(tokenList[1].stringContent)

        if isinstance(tokenList[0], LabelKeyword):
            return DeclaringLabel(tokenList[1].stringContent)

        # jump and call
        if isinstance(tokenList[0], GotoKeyword):
            return JumpStatement(tokenList[1].stringContent)

        if isinstance(tokenList[0], CallKeyword):
            return CallStatement(tokenList[1].stringContent)

    elif len(tokenList) == 3:
        if isinstance(tokenList[0], AnythingElse):
            # left side is something that isnt a keyword
            if isinstance(tokenList[1], EqualsSymbol):
                # we are assigning something to something in here
                if isinstance(tokenList[2], IntegerLiteral):
                    return AssigningInteger(tokenList[2].stringContent, [tokenList[0]])

                if isinstance(tokenList[2], FloatLiteral):
                    return AssigningFloat(tokenList[2].stringContent, [tokenList[0]])

                if isinstance(tokenList[2], AnythingElse):
                    return AssigningVariableToVariable(subTokens=[tokenList[0], tokenList[2]])

            if isinstance(tokenList[1], AddSymbol):
                return AdditionStatement(subTokens=[tokenList[0], tokenList[2]])

            if isinstance(tokenList[1], MinusSymbol):
                return MinusStatement(subTokens=[tokenList[0], tokenList[2]])

            if isinstance(tokenList[1], MultiplySymbol):
                return MultiplyStatement(subTokens=[tokenList[0], tokenList[2]])

            if isinstance(tokenList[1], DivideSymbol):
                return DivideStatement(subTokens=[tokenList[0], tokenList[2]])

            if isinstance(tokenList[1], ModuloSymbol):
                return ModuloStatement(subTokens=[tokenList[0], tokenList[2]])

            if isinstance(tokenList[1], BitwiseNotSymbol):
                return UnaryNotStatement(subTokens=[tokenList[0], tokenList[2]])

    elif len(tokenList) == 4:
        # if with comparison
        if isinstance(tokenList[0], IfKeyword):
            if isinstance(tokenList[2], IsKeyword):
                return IfEqualityStatement(subTokens=[tokenList[1], tokenList[3]])

            if isinstance(tokenList[2], LessThanSymbol):
                return IfLessThanStatement(subTokens=[tokenList[1], tokenList[3]])

            if isinstance(tokenList[2], GreaterThanSymbol):
                return IfGreaterThanStatement(subTokens=[tokenList[1], tokenList[3]])

    somethingElseString = ""

    for tk in tokenList:
        somethingElseString += tk.stringContent

    return SomethingElseInternal(somethingElseString)

# this takes a list of tokens that have come from stage 1, and finds blocks to combine into one token with sub tokens
def combineIfPossibleStage2(tokenList: list[Token | InternalToken]) -> list[Token | InternalToken]:
    globalTokenScope: list[Token | InternalToken] = []

    blockStack: list[BlockExpression] = []

    for tk in tokenList:
        if isinstance(tk, OpenCurlySymbol):
            newBlock = BlockExpression()

            if len(blockStack):
                blockStack[-1].subTokens.append(newBlock)

            blockStack.append(newBlock)

        elif isinstance(tk, ClosingCurlySymbol):
            if len(blockStack):
                globalTokenScope.append(blockStack.pop())
            else:
                globalTokenScope.append(InternalErrorToken("unmatched closing curly"))

        else:
            if len(blockStack):
                blockStack[-1].subTokens.append(tk)

            else:
                globalTokenScope.append(tk)

    return globalTokenScope

# this takes the output of stage 2 and attempts to combine ifs and whiles with a block to turn them into a single token
def combineIfPossibleStage3(tokenList: list[Token | InternalToken]) -> list[Token | InternalToken]:
    ...
