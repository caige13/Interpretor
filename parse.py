from lexer import Lexer, Tok
from symbol_table import FunctionSymbolTable

class Parse():
    def __init__(self, input):
        self.nextToken = []
        self.lexer = Lexer(input)
        # certain keyword will add and take away from scope
        self.cur_scope = "main"
        self.FunctionTable = FunctionSymbolTable()

    def __parseError(self, msg, handle_semicolon=False):
        if handle_semicolon:
            print("Parse Error: " + msg + " at line " + str(self.lexer.line-1))
        else:
            print("Parse Error: " + msg + " at line " + str(self.lexer.line))

    def __lex(self):
        self.nextToken = self.lexer.lex()
        if self.nextToken[0]==Tok.ERROR:
            print("Lex Error: "+str(self.nextToken[1]))
            exit()

    def __parseReturn_Option(self):
        if self.__parseStr_Expr():
            return True
        elif self.__parseInt_Expr():
            return True
        else:
            return False

    def __parseReturn(self):
        if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="return":
            if self.__parseReturn_Option():
                if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==";":
                    self.__parseError("There should not be a semi colon after a return statement")
                    return False
                else:
                    return True
            else:
                self.__parseError("Must return something that is a string or integer expression")
                return False
        else:
            self.lexer.saveToken(self.nextToken)
            return True

    def __parseAmbiguous(self):
        if self.nextToken[0]==Tok.ID:
            return self.__parseID_Operation()
        else:
            return False

    def __parseRaw_Nonint(self):
        if self.nextToken[0]==Tok.STRING:
            return True
        elif self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="str":
            self.__lex()
            if self.nextToken[0]==Tok.OPENPARENTHESIS:
                self.__lex()
                if self.__parseValue():
                    self.__lex()
                    if self.nextToken[0]==Tok.CLOSEPARENTHESIS:
                        return True
                    else:
                        self.__parseError("Expected ')' to end casting statement to a string")
                        return False
                else:
                    self.__parseError("Expected to cast a value(int, string, ID) but was given '"+str(self.nextToken[1])+"'")
                    return False
            else:
                self.__parseError("Expected '(' after 'str' and before the value to cast")
                return False
        else:
            return False

    def __parseRaw_Int(self):
        if self.nextToken[0]==Tok.INT:
            return True
        elif self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="int":
            self.__lex()
            if self.nextToken[0]==Tok.OPENPARENTHESIS:
                self.__lex()
                if self.__parseValue():
                    self.__lex()
                    if self.nextToken[0]==Tok.CLOSEPARENTHESIS:
                        return True
                    else:
                        self.__parseError("Expected ')' to end casting statement to an int")
                        return False
                else:
                    self.__parseError("Expected to cast a value(int, string, ID) but was given '"+str(self.nextToken[1])+"'")
                    return False
            else:
                self.__parseError("Expected '(' after 'int' and before the value to cast")
                return False
        else:
            return False

    def __parseInt_Value(self):
        if self.__parseRaw_Int():
            return True
        elif self.nextToken[0]==Tok.SUBTRACT:
            self.__lex()
            return self.__parseInt_Value()
        elif self.nextToken[0]==Tok.ADD:
            self.__lex()
            return self.__parseInt_Value()
        elif self.__parseAmbiguous():
            return True
        else:
            self.__parseError("Either a int or ID is not given or there was a error and additional info has been given")
            return False

    def __parseNonint_Value(self):
        if self.__parseRaw_Nonint():
            return True
        elif self.__parseAmbiguous():
            return True
        else:
            self.__parseError("Expected either a literal String, a cast to a string, or an ID or there was a error and additional info has been given")
            return False

    def __parseValue(self):
        if self.__parseRaw_Nonint():
            return True
        elif self.__parseRaw_Int():
            return True
        elif self.__parseAmbiguous():
            return True
        else:
            self.__parseError(
                "Expected a correctly formatted cast, int, string, or ID(array, variable, function call) but received '" +
                str(self.nextToken[1]) + "'")
            return False

    def __parseID_Operation(self):
        self.__lex()
        if self.nextToken==Tok.LEXEME and self.nextToken[1]=="[":
            if self.__parseInt_Value():
                self.__lex()
                if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]=="]":
                    return True
                else:
                    self.__parseError("Expected ']' to close array access")
                    return False
            else:
                return False
        elif self.nextToken[0]==Tok.OPENPARENTHESIS:
            if self.__parseParams():
                self.__lex()
                if self.nextToken[0]==Tok.CLOSEPARENTHESIS:
                    return True
                else:
                    self.__parseError("Expected ')' to close function call")
                    return False
            else:
                return False
        else:
            self.lexer.saveToken(self.nextToken)
            return True

    def __parseFactor(self):
        if self.__parseInt_Value():
            if self.__parseCompare():
                return True
            else:
                return False
        else:
            return False

    def __parseSecond_Degree(self):
        self.__lex()
        if self.nextToken[0]==Tok.MULTIPLY:
            self.__lex()
            return self.__parseTerm()
        elif self.nextToken[0]==Tok.DIVIDE:
            self.__lex()
            return self.__parseTerm()
        elif self.nextToken[0]==Tok.MODULO:
            self.__lex()
            return self.__parseTerm()
        else:
            self.lexer.saveToken(self.nextToken)
            return True

    def __parseFirst_Degree(self):
        self.__lex()
        if self.nextToken[0]==Tok.ADD:
            self.__lex()
            return self.__parseN_Expr()
        elif self.nextToken[0]==Tok.SUBTRACT:
            self.__lex()
            return self.__parseN_Expr()
        else:
            self.lexer.saveToken(self.nextToken)
            return True

    def __parseLogic(self):
        self.__lex()
        if self.nextToken[0]==Tok.AND:
            self.__lex()
            return self.__parseN_Expr()
        elif self.nextToken[0]==Tok.OR:
            self.__lex()
            return self.__parseN_Expr()
        else:
            self.lexer.saveToken(self.nextToken)
            return True

    def __parseCompare(self):
        self.__lex()
        if self.nextToken[0]==Tok.COMPARESYMBOL:
            self.__lex()
            if self.__parseInt_Value():
                return True
            else:
                return False
        else:
            self.lexer.saveToken(self.nextToken)
            return True

    def __parseStr_OperationMult(self):
        self.__lex()
        return self.__parseNonint_Value()

    def __parseStr_Operation(self):
        self.__lex()
        if self.nextToken[0]==Tok.ADD:
            if self.__parseStr_OperationMult():
                return self.__parseStr_Operation()
            else:
                self.__parseError("Expected a String to concat with")
        else:
            self.lexer.saveToken(self.nextToken)
            return True

    def __parseTerm(self):
        if self.__parseFactor():
            if self.__parseSecond_Degree():
                return True
            else:
                return False
        else:
            return False

    def __parseN_Expr(self):
        if self.__parseTerm():
            if self.__parseFirst_Degree():
                return True
            else:
                return False
        else:
            return False

    def __parseInt_Expr(self):
        self.__lex()
        if self.__parseN_Expr():
            if self.__parseLogic():
                return True
            else:
                return False
        else:
            return False

    def __parseStr_Expr(self):
        self.__lex()
        if self.__parseNonint_Value():
            if self.__parseStr_Operation():
                return True
            else:
                self.__parseError("Expected a string operation but received '"+str(self.nextToken[1])+"'")
                return False
        else:
            return False


    # Mult is used instead of ' if you are doing a direct comparison to the grammar.
    def __parseParamsMult(self):
        self.__lex()
        if self.nextToken[0] == Tok.CLOSEPARENTHESIS and self.nextToken[1] == ")":
            return True
        elif self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==",":
            self.__lex()
            if self.nextToken[0]==Tok.ID:
                return self.__parseParamsMult()
            else:
                self.__parseError("Expected an ID but received '"+str(self.nextToken[1])+"'")
                return False
        else:
            self.__parseError("Expected ',' or ')' for function definition")
            return False

    def __parseParams(self):
        self.__lex()
        if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == ")":
            return True
        elif self.nextToken[0]==Tok.ID:
            return self.__parseParamsMult()
        else:
            self.__parseError("Expected ')' or ID as parameters")
            return False

    # Mult is used instead of ' if you are doing a direct comparison to the grammar.
    def __parseStr_ArgMult(self):
        if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "]":
            return True
        self.__lex()
        if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == ",":
            if self.__parseStr_Expr():
                return self.__parseStr_ArgMult()
            else:
                self.__parseError("Expected String expression as array arguments")
                return False

    def __parseStr_Arg(self):
        if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "]":
            return True
        elif self.__parseStr_Expr():
            return self.__parseStr_ArgMult()
        else:
            self.__parseError("Expected string expression as array arguments")
            return False

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
            self.__parseError("Expected ']' to finish the array assignment but got '"+str(self.nextToken[1])+"'")
            return False

    def __parseInt_Arg(self):
        self.__lex()
        if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "]":
            return True
        self.lexer.saveToken(self.nextToken)
        if self.__parseInt_Expr():
            return self.__parseInt_ArgMult()
        else:
            self.__parseError("Expected int expression as array arguments")
            return False

    def __parseAssign_Stropt(self):
        self.__lex()
        if self.nextToken[0] == Tok.ID:
            self.__lex()
            if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "=":
                self.__lex()
                if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "[":
                    if self.__parseStr_Arg():
                        if self.lexer.tokenSaved != -1:
                            self.__lex()
                            return True
                        else:
                            return True
                    else:
                        return False
                self.lexer.saveToken(self.nextToken)
                if self.__parseStr_Expr():
                    return True
                else:
                    self.__parseError("Expected Array Assignment or string expression, but got '" + str(self.nextToken[1]) + "'")
            else:
                self.__parseError("Expected '=' sign in assignment statement")
                return False
        else:
            self.__parseError("No ID was given to assign to")
            return False

    def __parseAssign_Intopt(self):
        self.__lex()
        if self.nextToken[0]==Tok.ID:
            self.__lex()
            if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]=="=":
                self.__lex()
                if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]=="[":
                    if self.__parseInt_Arg():
                        if self.lexer.tokenSaved != -1:
                            self.__lex()
                            return True
                        else:
                            return True
                    else:
                        return False
                self.lexer.saveToken(self.nextToken)
                if self.__parseInt_Expr():
                    return True
                else:
                    self.__parseError("Expected Array Assignment or int expression, but got '"+str(self.nextToken[1])+"'")
                    return False
            else:
                self.__parseError("Expected '=' sign in assignment statement")
                return False
        else:
            self.__parseError("No ID was given to assign to")
            return False

    def __parseIf_Options(self):
        if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "end":
            return True
        elif self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="elif":
            if self.__parseInt_Expr():
                self.__lex()
                if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "then":
                    self.__lex()
                    if self.__parseStmt_List():
                        if self.__parseIf_Options():
                            return True
                        else:
                            self.__parseError("Expected 'elif', 'else', or 'end' but received '" + str(self.nextToken[1]))
                            return False
                    else:
                        return False
                else:
                    self.__parseError("Expected the keyword 'then' after the if condition")
                    return False
            else:
                self.__parseError("Expected a Integer expression for the if condition")
                return False
        elif self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="else":
            self.__lex()
            if self.__parseStmt_List():
                if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "end":
                    return True
                else:
                    self.__parseError("Expected 'end' to finish the if statement")
                    return False
            else:
                return False
        else:
            self.__parseError("Expected 'end' to finish the if statement")
            return False

    def __parsePrntf_Expr(self, printfSub):
        self.__lex()
        if self.nextToken[0] != Tok.CLOSEPARENTHESIS and len(printfSub)==0:
            self.__parseError("The 'printf' statement likely has more arguments than '%s' or '%d'")
            return False
        if self.nextToken[0] == Tok.CLOSEPARENTHESIS and len(printfSub)!=0:
            self.__parseError("The 'printf' statement likely has less arguments than '%s' or '%d'")
            return False
        if self.nextToken[0] == Tok.CLOSEPARENTHESIS and len(printfSub)==0:
            return True
        if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==",":
            self.__lex()
            if self.__parseValue():
                return self.__parsePrntf_Expr(printfSub[1:])
            else:
                self.__parseError("Expected a Value(ID, String, Int) but did not receive one in the 'printf' statement")
                return False
        else:
            self.__parseError("Expected ',' or ')' but got '"+str(self.nextToken[1])+"' in the 'printf' statement")
            return False


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
            self.__parseError("Invalid Source Code: "+str(self.nextToken[1])+"'")
            return False

    def __parsePrnt_Arg(self):
        self.__lex()
        if self.nextToken[0] == Tok.CLOSEPARENTHESIS:
            return True
        elif self.__parseValue():
            return self.__parsePrnt_Expr()
        else:
            self.__parseError("Invalid Source Code: " + str(self.nextToken[1])+"'")
            return False

    def __parseFunction_Def(self):
        self.__lex()
        if self.nextToken[0]==Tok.ID:
            ID = self.nextToken[1]
            self.__lex()
            if self.nextToken[0]==Tok.OPENPARENTHESIS and self.nextToken[1]=="(":
                if self.__parseParams():
                    self.__lex()
                    if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="begin":
                        self.cur_scope = ID

                        self.__lex()
                        if self.__parseStmt_List():
                            if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "end":
                                return True
                            if self.__parseReturn():
                                self.__lex()
                                if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="end":
                                    return True
                                else:
                                    self.__parseError("Expected 'end' to finish the Function")
                                    return False
                            else:
                                return False
                        else:
                            return False
                    else:
                        self.__parseError("Expected the 'begin' keyword")
                        return False
                else:
                    return False
            else:
                self.__parseError("Expected '('")
                return False
        else:
            self.__parseError("Expected a ID(name for function) but received '"+str(self.nextToken[1])+"'")
            return False

    def __parseFor(self):
        self.__lex()
        if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="int":
            if self.__parseAssign_Intopt():
                self.__lex()
                if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==";":
                    if self.__parseInt_Expr():
                        self.__lex()
                        if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == ";":
                            if self.__parseInt_Expr():
                                self.__lex()
                                if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "do":
                                    self.__lex()
                                    if self.__parseStmt_List():
                                        if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "end":
                                            return True
                                        else:
                                            self.__parseError("Expected 'end' to finish the 'for' loop statement")
                                            return False
                                    else:
                                        return False
                                else:
                                    self.__parseError("Expected the 'do' keyword after the initialization of the 'for' loop")
                                    return False
                            else:
                                self.__parseError("Expected a Integer expression for the for loop step size")
                                return False
                        else:
                            self.__parseError("Expected a ';' after the condition in the 'for' loop")
                            return False
                    else:
                        self.__parseError("Expected a Integer expression for the 'for' loop condition")
                        return False
                else:
                    self.__parseError("Expected a ';' after the initialization of the control variable in the 'for' loop")
                    return False
            else:
                return False
        else:
            self.__parseError("Must initialize a integer variable to be the control variable")
            return False

    def __parseWhile(self):
        if self.__parseInt_Expr():
            self.__lex()
            if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="do":
                self.__lex()
                if self.__parseStmt_List():
                    if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="end":
                        return True
                    else:
                        self.__parseError("Expected 'end' to finish the while loop statement")
                        return False
                else:
                    return False
            else:
                self.__parseError("Expected the 'do' keyword after the condition of the while loop")
                return False
        else:
            self.__parseError("Expected a Integer expression for the while loop condition")

    def __parseIf(self):
        if self.__parseInt_Expr():
            self.__lex()
            if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "then":
                self.__lex()
                if self.__parseStmt_List():
                    if self.__parseIf_Options():
                       return True
                    else:
                        self.__parseError("Expected 'elif', 'else', or 'end' but received '" + str(self.nextToken[1]))
                        return False
                else:
                    return False
            else:
                self.__parseError("Expected the keyword 'then' after the if condition")
                return False
        else:
            self.__parseError("Expected a Integer expression for the if condition")
            return False

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
            self.__parseError("Expected '{', ',' or ';', but received '"+str(self.nextToken[1])+"' for the 'get' statement")
            return False

    def __parseInput(self):
        self.__lex()
        if self.nextToken[0]==Tok.ID:
            return self.__parseInput_Mult()
        else:
            self.__parseError("Expected an ID but got '"+str(self.nextToken[1])+"'")
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

    def __parseFunction_Call(self):
        self.__lex()
        if self.nextToken[0]==Tok.OPENPARENTHESIS:
            return self.__parseParams()
        else:
            self.__parseError("Expected '(' after function name")


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
        elif self.nextToken[0] == Tok.ID:
            return self.__parseFunction_Call()
        elif self.nextToken[0] == Tok.KEYWORD and (self.nextToken[1] == "end" or self.nextToken[1] == "return"
                or self.nextToken[1] == "elif" or self.nextToken[1] == "else"):
            return False
        else:
            self.__parseError("The Statement Provided is not recognized")
            return False

    def __parseStmt_List(self):
        if self.nextToken[0] == Tok.END_OF_INPUT:
            return True
        if self.__parseStmt():
            self.__lex()
            if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == ";":
                self.__lex()
                return self.__parseStmt_List()
            else:
                self.__parseError("Expected a semicolon", True)
                return False
        # stmt_list has empty string as base case which cant really be replicated in
        # implementation so this is the work around.
        elif self.nextToken[0]==Tok.KEYWORD and (self.nextToken[1]=="end" or self.nextToken[1] == "return" or
                self.nextToken[1] == "elif" or self.nextToken[1] == "else"):
            return True
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