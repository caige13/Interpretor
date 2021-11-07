from lexer import Lexer, Tok

class Parse():
    def __init__(self, input):
        self.nextToken = []
        self.lexer = Lexer(input)
        # certain keyword will add and take away from scope
        self.cur_scope = "main"

    def __parseError(self, msg):
        print("Parse Error: " + msg + " at line " + str(self.lexer.line))

    def __lex(self):
        self.nextToken = self.lexer.lex()

    def __parseReturn_Option(self):
        return

    def __parseReturn(self):
        return

    def __parseAmbiguous(self):
        return

    def __parseRaw_Nonint(self):
        return

    def __parseRaw_Int(self):
        return

    def __parseInt_Value(self):
        return

    def __parseNonint_Value(self):
        return

    def __parseValue(self):
        return

    def __parseID_Operation(self):
        return

    def __parseFactor(self):
        return

    def __parseSecond_Degree(self):
        return

    def __parseFirst_Degree(self):
        return

    def __parseLogic(self):
        return

    def __parseCompare(self):
        return

    def __parseStr_OperationMult(self):
        return

    def __parseStr_Operation(self):
        return

    def __parseTerm(self):
        return

    def __parseN_Expr(self):
        return

    def __parseInt_Expr(self):
        return

    def __parseStr_Expr(self):
        return

    # Mult is used instead of ' if you are doing a direct comparison to the grammar.
    def __parseParmsMult(self):
        return

    def __parseParams(self):
        return

    # Mult is used instead of ' if you are doing a direct comparison to the grammar.
    def __parseStr_ArgMult(self):
        return

    def __parseStr_Arg(self):
        return

    #Mult is used instead of ' if you are doing a direct comparison to the grammar.
    def __parseInt_ArgMult(self):
        if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "]":
            return True
        self.__lex()
        if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==",":
            if self.__parseInt_Expr():
                return self.__parseInt_ArgMult()
            else:
                self.__parseError("Expected int expression as array arguments")
                return False
        else:
            self.__parseError("Expected ']' to finish the array assignment but got '"+self.nextToken[1]+"'")
            return False

    def __parseInt_Arg(self):
        if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "]":
            return True
        elif self.__parseInt_Expr():
            return self.__parseInt_ArgMult()
        else:
            self.__parseError("Expected int expression as array arguments")
            return False

    def __parseAssign_Stropt(self):
        return

    def __parseAssign_Intopt(self):
        if self.__parseInt_Expr():
            return True
        self.__lex()
        if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]=="[":
            return self.__parseInt_Arg()
        else:
            self.__parseError("Expected Array Assignment or int expression, but got '"+self.nextToken[1]+"'")

    def __parseIf_Options(self):
        return

    def __parsePrntf_Expr(self, printfSub):
        self.__lex()
        if self.nextToken[0] != Tok.CLOSEPARENTHESIS and len(printfSub)==0:
            self.__parseError("The 'printf' statement likely has more arguments than '%s' or '%d'")
            return False
        elif self.nextToken[0] == Tok.CLOSEPARENTHESIS and len(printfSub)!=0:
            self.__parseError("The 'printf' statement likely has less arguments than '%s' or '%d'")
            return False
        elif self.nextToken[0] == Tok.CLOSEPARENTHESIS and len(printfSub)==0:
            return True
        elif self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==",":
            if self.__parseValue():
                return self.__parsePrntf_Expr(printfSub[1:])
            else:
                self.__parseError("Expected a Value(ID, String, Int) but did not receive one in the 'printf' statement")
        else:
            self.__parseError("Expected ',' or ')' but got '"+self.nextToken[1]+"' in the 'printf' statement")


    def __parsePrntf_Arg(self):
        self.__lex()
        if self.nextToken[0] == Tok.STRING:
            return True
        elif self.nextToken[0] == Tok.FSTRING:
            return self.__parsePrntf_Expr(self.nextToken[2:])
        else:
            self.__parseError("Expected a literal String value to begin the 'printf' statement. Otherwise use 'print'.")

    def __parsePrnt_Expr(self):
        self.__lex()
        if self.nextToken[0]==Tok.CLOSEPARENTHESIS:
            return True
        elif self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==",":
            self.__lex()
            if self.__parseValue():
                return self.__parsePrnt_Expr()
        elif self.__parseStr_Operation():
            return self.__parsePrnt_Expr()
        else:
            self.__parseError("Invalid Source Code: "+self.nextToken[1])
            return False

    def __parsePrnt_Arg(self):
        self.__lex()
        if self.nextToken[0] == Tok.CLOSEPARENTHESIS:
            return True
        elif self.__parseValue():
            return self.__parsePrnt_Expr()
        else:
            self.__parseError("Invalid Source Code: " + self.nextToken[1])
            return False

    def __parseFunction_Def(self):
        return

    def __parseFor(self):
        return

    def __parseWhile(self):
        return

    def __parseIf(self):
        return

    def __parseInput_Mult(self):
        self.__lex()
        if self.nextToken[0]==Tok.LEXEME and self.nextToken=="{":
            self.__lex()
            if self.nextToken[0]==Tok.STRING:
                self.__lex()
                if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]=="}":
                    return self.__parseInput_Mult()
                else:
                    self.__parseError("Expected a '}' to close off the message in get")
                    return False
            else:
                self.__parseError("Expected a string after '{'")
                return False
        elif self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==",":
            if self.nextToken[0]==Tok.ID:
                return self.__parseInput_Mult()
            else:
                self.__parseError("Expected an ID(String, Variable, Int) after ','")
                return False
        elif self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==";":
            self.lexer.saveToken(self.nextToken)
            return True
        else:
            self.__parseError("Expected '{', ',' or ';', but received '"+self.nextToken[1]+"' for the 'get' statement")
            return False

    def __parseInput(self):
        self.__lex()
        if self.nextToken[0]==Tok.ID:
            return self.__parseInput_Mult()
        else:
            self.__parseError("Expected an ID but got '"+self.nextToken[1]+"'")
            return False

    def __parsePrintf(self):
        self.__lex()
        if self.nextToken[0]==Tok.OPENPARENTHESIS:
            return self.__parsePrntf_Arg()
        else:
            self.__parseError("The statement 'printf' has been called without an open parenthesis, '('.")
            return False

    def __parsePrint(self):
        self.__lex()
        if self.nextToken[0]==Tok.OPENPARENTHESIS:
            return self.__parsePrnt_Arg()
        else:
            self.__parseError("The statement 'print' has been called without an open parenthesis, '('.")
            return False

    def __parseStmt(self):
        if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "print":
            return self.__parsePrint()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "printf":
            return self.__parsePrintf()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "get":
            return self.__parseInput()
        # assign for integer
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "int":
            return self.__parseAssign_Intopt()
        # assign for string
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "str":
            return self.__parseAssign_Stropt()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "if":
            return self.__parseIf()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "while":
            return self.__parseWhile()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "for":
            return self.__parseFor()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "def":
            return self.__parseFunction_Def()

    def __parseStmt_List(self):
        if self.nextToken[0] == Tok.END_OF_INPUT:
            return True
        if self.__parseStmt():
            self.__lex()
            if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == ";":
                self.__lex()
                return self.__parseStmt_List()
        else:
            return False

    def __parseProg(self):
        return self.__parseStmt_List()

    def parse(self):
        self.__lex()

        if self.nextToken[0] == Tok.ERROR:
            print("Lex Error: ", self.nextToken[1])
        else:
            if self.__parseProg():
                    if self.nextToken[0] != Tok.END_OF_INPUT:
                        print("Parse Error: Unrecognized trailing characters")
                    else:
                        print("Valid Program")