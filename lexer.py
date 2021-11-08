import enum
import sys
import re

# Tokens enum
class Tok(enum.Enum):
    STRING = 0
    INT = 1
    ERROR = 2
    END_OF_INPUT = 3
    ID = 4
    LEXEME = 5
    KEYWORD = 6
    OPENPARENTHESIS = 7
    CLOSEPARENTHESIS = 8
    ADD = 9
    SUBTRACT = 10
    DIVIDE = 11
    MODULO = 12
    MULTIPLY = 13
    AND = 14
    OR = 15
    FSTRING = 16
    COMPARESYMBOL = 17

class Lexer():
    def __init__(self, source_code: str):
        self.input = source_code
        self.line = 1
        self.index = 0
        self.tokenSaved = -1

    def __lookUp(self, lexeme):
        # First this is better than just a long if statement. Second I can map a keyword to a specific Token
        # if I so please to implement that in the future it would be a easy addition.
        keywords = { "if": Tok.KEYWORD, "elif": Tok.KEYWORD, "else": Tok.KEYWORD, "get": Tok.KEYWORD,
                     "print": Tok.KEYWORD, "for": Tok.KEYWORD, "while": Tok.KEYWORD, "do": Tok.KEYWORD,
                     "begin": Tok.KEYWORD, "end": Tok.KEYWORD, "and": Tok.AND, "or": Tok.OR, "str": Tok.KEYWORD,
                     "int": Tok.KEYWORD, "printf": Tok.KEYWORD, "def": Tok.KEYWORD, "return": Tok.KEYWORD,
                     "then": Tok.KEYWORD}
        if lexeme in keywords:
            return [keywords[lexeme], lexeme]
        else:
            return [Tok.ID, lexeme]

    def __lexInt(self, sign):
        if(self.input[self.index] == "-" or self.input[self.index] == "+"):
            i = self.index + 1
            self.index += 1
        else:
            i = self.index
        while i < len(self.input) and self.input[i].isspace():
            if self.input[self.index] == "\n":
                return [Tok.ERROR, "New Line found in the middle of a statement at line " + str(self.line)]
            i += 1
        while i < len(self.input) and self.input[i].isdigit():
            i += 1
        response = [Tok.INT, sign * int("".join(self.input[self.index:i]))]
        self.index = i
        return response

    def __isIdChar(self, c):
        return c == "_" or c.isalpha() or c.isdigit()

    def __lexIdOrKeyword(self):
        i = self.index
        while i< len(self.input) and self.__isIdChar(self.input[i]):
            i = i + 1
        temp = self.__lookUp("".join(self.input[self.index:i]))
        self.index = i
        return temp

    def __ParseOutString(self):
        i = self.index+1
        content = ""
        while(self.input[i] != "\""):
            content += self.input[i]
            i = i+1
            if i >= len(self.input):
                return [Tok.ERROR, "Missing end quote for string on line: " + str(self.line)]
        self.index = i + 1
        regex = re.compile("([%][d,s])+")
        result = regex.findall(content)
        if result:
            return_val = [Tok.FSTRING, "\""+content+"\""]
            for group in result:
                return_val.append(group)
            return return_val
        else:
            return [Tok.STRING, "\""+content+"\""]

    def saveToken(self, token):
        self.tokenSaved = token

    def lex(self):
        if self.tokenSaved != -1:
            temp = self.tokenSaved
            self.tokenSaved = -1
            return temp
        while self.index < len(self.input) and self.input[self.index].isspace():
            if self.input[self.index] == "\n":
                self.line = self.line +1
            self.index = self.index + 1
        if self.index >= len(self.input):
            return [Tok.END_OF_INPUT, ""]
        if self.input[self.index] == "=":
            if (self.index < len(self.input) and self.input[self.index + 1] == "="):
                self.index += 2
                return [Tok.COMPARESYMBOL, "=="]
            else:
                self.index += 1
                return [Tok.LEXEME, "="]
        elif self.input[self.index] == "!":
            if(self.index < len(self.input) and self.input[self.index+1] == "="):
                self.index += 2
                return [Tok.COMPARESYMBOL, "!="]
            else:
                return [Tok.ERROR, "Found ! without a '=' after it on line: "+str(self.line)]
        elif self.input[self.index] == ",":
            self.index += 1
            return [Tok.LEXEME, ","]
        elif self.input[self.index] == ";":
            self.index += 1
            return [Tok.LEXEME, ";"]
        elif self.input[self.index] == "/":
            self.index += 1
            return [Tok.DIVIDE, "/"]
        elif self.input[self.index] == "+":
            self.index += 1
            return [Tok.ADD, "+"]
        elif self.input[self.index] == "%":
            self.index += 1
            return [Tok.MODULO, "%"]
        elif self.input[self.index] == "-":
            self.index += 1
            return [Tok.SUBTRACT, "-"]
        elif self.input[self.index] == "*":
            self.index += 1
            return [Tok.MULTIPLY, "*"]
        elif self.input[self.index] == "<":
            if (self.index < len(self.input) and self.input[self.index + 1] == "="):
                self.index += 2
                return [Tok.COMPARESYMBOL, "<="]
            else:
                self.index += 1
                return [Tok.COMPARESYMBOL, "<"]
        elif self.input[self.index] == ">":
            if (self.index < len(self.input) and self.input[self.index + 1] == "="):
                self.index += 2
                return [Tok.COMPARESYMBOL, ">="]
            else:
                self.index += 1
                return [Tok.COMPARESYMBOL, ">"]
        elif self.input[self.index].isdigit():
            return self.__lexInt(1)
        elif self.input[self.index] == ")":
            self.index += 1
            return [Tok.CLOSEPARENTHESIS, ")"]
        elif self.input[self.index] == "(":
            self.index += 1
            return [Tok.OPENPARENTHESIS, "("]
        elif self.input[self.index] == "[":
            self.index += 1
            return [Tok.LEXEME, "["]
        elif self.input[self.index] == "]":
            self.index += 1
            return [Tok.LEXEME, "]"]
        elif self.input[self.index] == "{":
            self.index +=1
            return [Tok.LEXEME, "{"]
        elif self.input[self.index] == "}":
            self.index += 1
            return [Tok.LEXEME, "}"]
        elif self.input[self.index] == "\"":
            return self.__ParseOutString()
        elif self.input[self.index] == "_" or self.input[self.index].isalpha():
            # Transition on an underscore or a letter
            return self.__lexIdOrKeyword()
        else:
            return [Tok.ERROR, "Unexpected character '" + self.input[self.index] + "' on line " + str(self.line)]