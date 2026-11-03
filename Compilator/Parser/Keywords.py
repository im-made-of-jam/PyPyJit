from .Token import *

_keywordList = {
    "func":FunctionKeyword, # declares a function that can be called with "call" e.g. "func doSomething"
    "import":ImportKeyword, # imports a function to be called with "call". syntas is e.g. "import kernel32.ExitProcess"
    "label":LabelKeyword,   # declares a label to be a jump target. labels use a different namespace to variables
    "if":IfKeyword,         # e.g. "if condition". uses standard C truthiness
    "goto":GotoKeyword,     # immediately transfer execution to the position immediately following a label
    "call":CallKeyword,     # calls a function declared with "func" or imported. arguments must be variables, not literals
    "is":IsKeyword,         # same as "==" in other languages. currently unable to be used with literals
    "return":ReturnKeyword,

    "int":IntegerKeyword,   # declares a 64 bit signed integer
    "float":FloatKeyword,   # declares a 64 bit IEEE float
}

_tokenList = {
    "=":EqualsSymbol,       # used only for assignment e.g. "x = 1"

    # these are all mathematical operations
    # all of these imply setting the left hand side to the result of the operation
    # e.g. "x + y" would be the same as "x += y" in other languages
    # none of these accept literals yet
    "+":AddSymbol,
    "-":MinusSymbol,
    "*":MultiplySymbol,
    "/":DivideSymbol,
    "%":ModuloSymbol,
    "~":BitwiseNotSymbol, # except this which is unary not

    # these two are purely for if statements
    "<":LessThanSymbol,
    ">":GreaterThanSymbol,

    "{":OpenCurlySymbol,
    "}":ClosingCurlySymbol,
    "(":OpenRoundSymbol,
    ")":ClosingRoundSymbol,
}

def _checkValidExternName(word):
    splitWord = word.split(".")

    if len(splitWord) == 2:
        return True

    return False

def getTokenFromWord(word):
    # TODO strings

    # print(type(word), word)

    # try these first because otherwise floats and extern imports conflict with each other
    try:
        int(word)
        return IntegerLiteral(word)

    except ValueError:
        pass

    try:
        float(word)
        return FloatLiteral(word)

    except ValueError:
        pass

    # keywords are of utmost importance
    if word in _keywordList:
        return _keywordList[word](word)

    # followed closely by tokens
    elif word in _tokenList:
        return _tokenList[word](word)

    elif _checkValidExternName(word):
        return ExternalFunction(word)

    return AnythingElse(word)
