class Token:
    def __init__(self, stringContent: str ="", subTokens: list | None = None, originalSourceLine: int = 0):
        self.stringContent = stringContent
        self.subTokens = subTokens if subTokens is not None else list()

        self.originalSourceLine = originalSourceLine

# keywords

class FunctionKeyword(Token):
    pass

class ImportKeyword(Token):
    pass

class LabelKeyword(Token):
    pass

class IfKeyword(Token):
    pass

class GotoKeyword(Token):
    pass

class CallKeyword(Token):
    pass

class IsKeyword(Token):
    pass


# symbols

class SemicolonSymbol(Token):
    pass

class EqualsSymbol(Token):
    pass

class AddSymbol(Token):
    pass

class MinusSymbol(Token):
    pass

class MultiplySymbol(Token):
    pass

class DivideSymbol(Token):
    pass

class ModuloSymbol(Token):
    pass

class BitwiseNotSymbol(Token):
    pass

class LessThanSymbol(Token):
    pass

class GreaterThanSymbol(Token):
    pass


class OpenCurlySymbol(Token):
    pass

class ClosingCurlySymbol(Token):
    pass

class OpenRoundSymbol(Token):
    pass

class ClosingRoundSymbol(Token):
    pass

# builtin types

class IntegerKeyword(Token):
    pass

class FloatKeyword(Token):
    pass

class ExternalFunction(Token):
    pass

# literal tokens e.g. "1" or "1.5"

class IntegerLiteral(Token):
    pass

class FloatLiteral(Token):
    pass

# the catch all token

class AnythingElse(Token):
    pass


# tokens for internal processing

# start with declarations

class InternalToken(Token):
    pass

class DeclaringInteger(InternalToken):
    pass

class DeclaringFloat(InternalToken):
    pass

class AssigningInteger(InternalToken):
    pass

class AssigningFloat(InternalToken):
    pass

class AssigningVariableToVariable(InternalToken):
    pass

class DeclaringFunction(InternalToken):
    pass

class DeclaringImport(InternalToken):
    pass

class DeclaringLabel(InternalToken):
    pass

# now onto statements

class JumpStatement(InternalToken):
    pass

class CallStatement(InternalToken):
    pass

class AdditionStatement(InternalToken):
    pass

class MinusStatement(InternalToken):
    pass

class MultiplyStatement(InternalToken):
    pass

class DivideStatement(InternalToken):
    pass

class ModuloStatement(InternalToken):
    pass

class UnaryNotStatement(InternalToken):
    pass

# this is an if with a variable ONLY
# e.g. "if x", as opposed to "if x is 2"
class IfSingleStatement(InternalToken):
    pass

# this is e.g. "if x is y"
class IfEqualityStatement(InternalToken):
    pass

# "if x < y"
class IfLessThanStatement(InternalToken):
    pass

# if "x > y"
class IfGreaterThanStatement(InternalToken):
    pass

# this is a token to encapsulate an entire block as one token with subtokens
class BlockExpression(InternalToken):
    pass

# some subtypes of that
class IfWithBlock(InternalToken):
    pass

# the catch all tokens

class SomethingElseInternal(InternalToken):
    pass

class InternalErrorToken(InternalToken):
    pass
