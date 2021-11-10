from lexer import Lexer, Tok
from symbol_table import FunctionSymbolTable, FuncSymbol, VarSymbol, LoopSymbol, VarSymbolTable


# NOTES: Potentially dont have to track variables in the Function Table but instead in a seperate Var Table.
# Every time you do a definition in the Var Table must check if the varaible already exists and if it does, we care
# about the scope and the type. Potential easy solution is to just not allow dynamic typing and variable cannot change
# Type. To do this when you realize a confliction check the types, if different error, if not then do something.
class Parse():
    def __init__(self, input):
        self.nextToken = []
        self.lexer = Lexer(input)
        # certain keyword will add and take away from scope
        self.cur_scope = "globe/main"
        self.scope_stack = []
        self.FunctionTable = FunctionSymbolTable()
        self.VarTable = VarSymbolTable()
        self.for_count = 0
        self.while_count = 0
        self.cache = -1

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

    def __parseReturn_Option(self, funcSymbol):
        self.__lex()
        if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "str":
            self.__lex()
            if self.nextToken[0]==Tok.CLOSEPARENTHESIS:
                if self.__parseStr_Expr():
                    return self.FunctionTable.updateType(funcSymbol, "string")
                else:
                    return False
            else:
                self.__parseError("Expected ')' to finish return type cast")
                return False
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "int":
            self.__lex()
            if self.nextToken[0]==Tok.CLOSEPARENTHESIS:
                if self.__parseInt_Expr():
                    return self.FunctionTable.updateType(funcSymbol, "integer")
                else:
                    return False
            else:
                self.__parseError("Expected ')' to finish return type cast")
                return False
        else:
            return False

    def __parseReturn_Cast(self, funcSymbol):
        self.__lex()
        if self.nextToken[0]==Tok.OPENPARENTHESIS:
            return self.__parseReturn_Option(funcSymbol)
        else:
            self.__parseError("Expected '(' after return to cast return type")
            return False

    def __parseReturn(self, funcSymbol):
        if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="return":
            if self.FunctionTable.updateType(funcSymbol, "true"):
                if self.__parseReturn_Cast(funcSymbol):
                    if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==";":
                        self.__parseError("There should not be a semi colon after a return statement")
                        return False
                    else:
                        return True
                else:
                    self.__parseError("Must return something that is a string or integer expression")
                    return False
            else:
                self.__parseError("There was a error inside the Function Symbol Table when Updating Type")
                return False
        else:
            self.lexer.saveToken(self.nextToken)
            return True

    def __parseAmbiguous(self, type_check):
        if self.nextToken[0]==Tok.ID:
            return self.__parseID_Operation(type_check)
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
        elif self.__parseAmbiguous("integer"):
            return True
        else:
            self.__parseError("Either a int or ID is not given or there was a error and additional info has been given")
            return False

    def __parseNonint_Value(self):
        if self.__parseRaw_Nonint():
            return True
        elif self.__parseAmbiguous("string"):
            return True
        else:
            self.__parseError("Expected either a literal String, a cast to a string, or an ID(String Type) or there was a error and additional info has been given")
            return False

    def __parseValue(self):
        if self.__parseRaw_Nonint():
            return True
        elif self.__parseRaw_Int():
            return True
        elif self.__parseAmbiguous("neutral"):
            return True
        else:
            self.__parseError(
                "Expected a correctly formatted cast, int, string, or ID(array, variable, function call) but received '" +
                str(self.nextToken[1]) + "'")
            return False

    def __parseID_Operation(self, type_check):
        ID = self.nextToken[1]
        self.__lex()
        if self.nextToken==Tok.LEXEME and self.nextToken[1]=="[":
            varSym = VarSymbol(name=ID, type=type_check, scope=self.cur_scope)
            exist_info = self.FunctionTable.findExistingInstance(varSym)
            if exist_info == -3:
                self.__parseError("Could not find the scope " + ID + " is in or a parent Scope")
                self.lexer.saveToken(self.nextToken)
                return False
            elif exist_info == -2:
                self.__parseError("Could not find the Variable table for the scope " + ID + " is in")
                self.lexer.saveToken(self.nextToken)
                return False
            elif exist_info == -1:
                self.__parseError(
                    "This language does not support Dynamic typing, " + ID + " has been defined else where with a different type")
                self.lexer.saveToken(self.nextToken)
                return False
            elif exist_info == 1:
                if self.__parseInt_Value():
                    self.__lex()
                    if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "]":
                        return True
                    else:
                        self.__parseError("Expected ']' to close array access")
                        return False
                else:
                    return False
            elif exist_info == 2:
                # The ID has not been defined already
                self.__parseError(ID+" has not been defined in this scope")
                self.lexer.saveToken(self.nextToken)
                return False
            else:
                self.__parseError("This should not be reached at all")
                self.lexer.saveToken(self.nextToken)
                return False
        elif self.nextToken[0]==Tok.OPENPARENTHESIS:
            # This means its a function call.
            # We must check ID in function table.
            check_function = self.FunctionTable.lookupFunction(ID)
            if check_function:
                if check_function[0].type == type_check:
                    if self.__parseCall_Params():
                        if self.nextToken[0] == Tok.CLOSEPARENTHESIS:
                            return True
                        else:
                            self.__parseError("Expected ')' to close function call")
                            self.lexer.saveToken(self.nextToken)
                            return False
                    else:
                        self.lexer.saveToken(self.nextToken)
                        return False
                else:
                    self.__parseError(ID+" Does not return the type expected")
                    self.lexer.saveToken(self.nextToken)
                    return False
            else:
                self.__parseError(ID+" has not been defined")
                self.lexer.saveToken(self.nextToken)
                return False
        else:
            varSym = VarSymbol(name=ID, type=type_check, scope=self.cur_scope)
            exist_info = self.FunctionTable.findExistingInstance(varSym)
            if exist_info == -3:
                self.__parseError("Could not find the scope " + ID + " is in or a parent Scope")
                self.lexer.saveToken(self.nextToken)
                return False
            elif exist_info == -2:
                self.__parseError("Could not find the Variable table for the scope " + ID + " is in")
                self.lexer.saveToken(self.nextToken)
                return False
            elif exist_info == -1:
                self.__parseError(
                    "This language does not support Dynamic typing, " + ID + " has been defined else where with a different type")
                self.lexer.saveToken(self.nextToken)
                return False
            elif exist_info == 1:
                self.lexer.saveToken(self.nextToken)
                return True
            elif exist_info == 2:
                # The ID has not been defined already
                self.__parseError(ID + " has not been defined in this scope")
                self.lexer.saveToken(self.nextToken)
                return False
            else:
                self.__parseError("This should not be reached at all")
                self.lexer.saveToken(self.nextToken)
                return False

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
                # Will pop up on return option potentially
                self.__parseError("Expected a string operation but received '"+str(self.nextToken[1])+"'")
                return False
        else:
            return False

    def __parseCall_ParamsMult(self):
        self.__lex()
        if self.nextToken[0] == Tok.CLOSEPARENTHESIS and self.nextToken[1] == ")":
            return True
        elif self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == ",":
            self.__lex()
            if self.__parseValue():
                return self.__parseCall_ParamsMult()
            else:
                self.__parseError("Expected an ID but received '" + str(self.nextToken[1]) + "'")
                return False
        else:
            self.__parseError("Expected ',' or ')' for function call")
            return False

    def __parseCall_Params(self):
        self.__lex()
        if self.nextToken[0] == Tok.CLOSEPARENTHESIS and self.nextToken[1] == ")":
            return True
        elif self.__parseValue():
            return self.__parseCall_ParamsMult()
        else:
            self.__parseError("Expected ')' or ID as parameters")
            return False

    # Mult is used instead of ' if you are doing a direct comparison to the grammar.
    def __parseParamsMult(self):
        self.__lex()
        if self.nextToken[0] == Tok.CLOSEPARENTHESIS and self.nextToken[1] == ")":
            return True
        elif self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==",":
            self.__lex()
            if self.nextToken[0]==Tok.ID:
                ID = self.nextToken[1]
                # This strategy works rather than having to search its scope ancestors because I designed the language
                # To only allow function to be made in a scope one below the global scope. Hence nested scopes not allowed.
                varSym = VarSymbol(name=ID, type="undefined", scope=self.cur_scope)
                funcSym = FuncSymbol(name=self.cur_scope.split("/")[-1], scope=self.cur_scope)
                out_table = self.FunctionTable.lookupByScope(funcSym)
                out_table[1].define(varSym)
                return self.__parseParamsMult()
            else:
                self.__parseError("Expected an ID but received '"+str(self.nextToken[1])+"'")
                return False
        else:
            self.__parseError("Expected ',' or ')' for function definition")
            return False

    def __parseParams(self):
        self.__lex()
        if self.nextToken[0] == Tok.CLOSEPARENTHESIS and self.nextToken[1] == ")":
            return True
        elif self.nextToken[0]==Tok.ID:
            ID = self.nextToken[1]
            # This strategy works rather than having to search its scope ancestors because I designed the language
            # To only allow function to be made in a scope one below the global scope. Hence nested scopes not allowed.
            varSym = VarSymbol(name=ID, type="undefined", scope=self.cur_scope)
            funcSym = FuncSymbol(name=self.cur_scope.split("/")[-1], scope=self.cur_scope)
            out_table = self.FunctionTable.lookupByScope(funcSym)
            out_table[1].define(varSym)
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
            ID = self.nextToken[1]
            self.__lex()
            if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "=":
                self.__lex()
                if self.nextToken[0] == Tok.LEXEME and self.nextToken[1] == "[":
                    if self.__parseStr_Arg():
                        if self.lexer.tokenSaved != -1:
                            self.__lex()
                            return [ID, True]
                        else:
                            return [ID, True]
                    else:
                        return [ID, False]
                self.lexer.saveToken(self.nextToken)
                if self.__parseStr_Expr():
                    return [ID, True]
                else:
                    self.__parseError("Expected Array Assignment or string expression, but got '" + str(self.nextToken[1]) + "'")
                    return [ID, False]
            else:
                self.__parseError("Expected '=' sign in assignment statement")
                return [ID, False]
        else:
            self.__parseError("No ID was given to assign to")
            return [0, False]

    def __parseAssign_Intopt(self):
        self.__lex()
        if self.nextToken[0]==Tok.ID:
            ID = self.nextToken[1]
            self.__lex()
            if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]=="=":
                self.__lex()
                if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]=="[":
                    if self.__parseInt_Arg():
                        if self.lexer.tokenSaved != -1:
                            self.__lex()
                            return [ID, True]
                        else:
                            return [ID, True]
                    else:
                        return [ID, False]
                self.lexer.saveToken(self.nextToken)
                if self.__parseInt_Expr():
                    return [ID, True]
                else:
                    self.__parseError("Expected Array Assignment or int expression, but got '"+str(self.nextToken[1])+"'")
                    return [ID, False]
            else:
                self.__parseError("Expected '=' sign in assignment statement")
                return [ID, False]
        else:
            self.__parseError("No ID was given to assign to")
            return [0, False]

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
            self.scope_stack.append(self.cur_scope)
            self.cur_scope = "globe/" + ID
            funcSymbol = FuncSymbol(ID)
            self.FunctionTable.defineFunction(funcSymbol)
            self.__lex()
            if self.nextToken[0]==Tok.OPENPARENTHESIS and self.nextToken[1]=="(":
                if self.__parseParams():
                    self.__lex()
                    if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="begin":
                        self.__lex()
                        if self.__parseStmt_List():
                            if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "end":
                                return True
                            if self.__parseReturn(funcSymbol):
                                self.__lex()
                                if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="end":
                                    self.cur_scope = self.scope_stack.pop()
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
            self.for_count = self.for_count + 1
            forSymbol = LoopSymbol(name="for"+str(self.for_count),scope=self.cur_scope)
            self.FunctionTable.defineFunction(forSymbol)
            self.scope_stack.append(self.cur_scope)
            self.cur_scope += "/for"+str(self.for_count)
            table_out = self.FunctionTable.lookupSymbol(forSymbol)
            ID, success = self.__parseAssign_Intopt()
            varSym = VarSymbol(name=ID, type="integer", scope=self.cur_scope)
            self.VarTable.define(varSym)
            table_out[1].define(varSym) # Choice made to not check if ID defined in prev. scopes to
                                        # default the loop counter to this Variable.
            if success:
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
                                            self.for_count -= 1
                                            self.FunctionTable.deleteEntry(forSymbol)
                                            self.cur_scope = self.scope_stack.pop()
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
        self.while_count += 1
        whileSymbol = LoopSymbol(name="while" + str(self.while_count), scope=self.cur_scope)
        self.FunctionTable.defineFunction(whileSymbol)
        self.scope_stack.append(self.cur_scope)
        if self.__parseInt_Expr():
            self.__lex()
            if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="do":
                self.cur_scope += "/while" + str(self.while_count)
                self.__lex()
                if self.__parseStmt_List():
                    if self.nextToken[0]==Tok.KEYWORD and self.nextToken[1]=="end":
                        self.while_count -= 1
                        self.FunctionTable.deleteEntry(whileSymbol)
                        self.cur_scope = self.scope_stack.pop()
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

    def __parseInput_Mult(self, IDs):
        self.__lex()
        if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]=="{":
            self.__lex()
            if self.nextToken[0]==Tok.STRING:
                self.__lex()
                if self.nextToken[0]==Tok.LEXEME and self.nextToken[1]=="}":
                    return self.__parseInput_Mult(IDs)
                else:
                    self.__parseError("Expected a '}' to close off the message in get")
                    return IDs, False
            else:
                self.__parseError("Expected a string after '{'")
                return IDs, False
        elif self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==",":
            self.__lex()
            if self.nextToken[0]==Tok.ID:
                IDs.append(self.nextToken[1])
                return self.__parseInput_Mult(IDs)
            else:
                self.__parseError("Expected an ID(String, Variable, Int) after ','")
                return IDs, False
        elif self.nextToken[0]==Tok.LEXEME and self.nextToken[1]==";":
            self.lexer.saveToken(self.nextToken)
            return IDs, True
        else:
            self.__parseError("Expected '{', ',' or ';', but received '"+str(self.nextToken[1])+"' for the 'get' statement")
            return IDs, False

    def __parseInput(self):
        self.__lex()
        if self.nextToken[0]==Tok.ID:
            ID = self.nextToken[1]
            varSym = VarSymbol(name=ID, type="string", scope=self.cur_scope)
            exist_info = self.FunctionTable.findExistingInstance(varSym)
            if exist_info == -3:
                self.__parseError("Could not find the scope " + ID + " is in or a parent Scope")
                return False
            elif exist_info == -2:
                self.__parseError("Could not find the Variable table to define " + ID + " in")
                return False
            elif exist_info == -1:
                self.__parseError(
                    "This language does not support Dynamic typing, " + ID + " has been defined else where with a different type")
                return False
            elif exist_info == 2:
                # The ID has not been defined already
                table_out = self.FunctionTable.lookupByScope(varSym)
                table_out[1].define(varSym)
            IDs = []
            IDs, success = self.__parseInput_Mult(IDs)
            for ID in IDs:
                varSym = VarSymbol(name=ID, type="string", scope=self.cur_scope)
                exist_info = self.FunctionTable.findExistingInstance(varSym)
                if exist_info == -3:
                    self.__parseError("Could not find the scope " + ID + " is in or a parent Scope")
                    return False
                elif exist_info == -2:
                    self.__parseError("Could not find the Variable table to define " + ID + " in")
                    return False
                elif exist_info == -1:
                    self.__parseError(
                        "This language does not support Dynamic typing, " + ID + " has been defined else where with a different type")
                    return False
                elif exist_info == 2:
                    # The ID has not been defined already
                    table_out = self.FunctionTable.lookupByScope(varSym)
                    table_out[1].define(varSym)
            return success
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
            return self.__parseCall_Params()
        else:
            self.__parseError("If meant for a function call: Expected '(' after function name\nIf meant for assignment did not include 'int' or 'str'")


    def __parseStmt(self):
        if self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "print":
            return self.__parsePrint()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "printf":
            return self.__parsePrintf()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "get":
            return self.__parseInput()
        # assign for integer
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "int":
            ID, success = self.__parseAssign_Intopt()
            if success:
                varSym = VarSymbol(name=ID, type="integer", scope=self.cur_scope)
                exist_info = self.FunctionTable.findExistingInstance(varSym)
                if exist_info == -3:
                    self.__parseError("Could not find the scope " + ID + " is in or a parent Scope")
                    return False
                elif exist_info == -2:
                    self.__parseError("Could not find the Variable table to define " + ID + " in")
                    return False
                elif exist_info == -1:
                    self.__parseError(
                        "This language does not support Dynamic typing, " + ID + " has been defined else where with a different type")
                    return False
                elif exist_info == 1:
                    # the ID has been defined already same type
                    return True
                elif exist_info == 2:
                    # The ID has not been defined already
                    table_out = self.FunctionTable.lookupByScope(varSym)
                    table_out[1].define(varSym)
                    return True
                else:
                    self.__parseError("This should not be reached at all")
                    return False
            else:
                return success
            # if success:
            #     varSym = VarSymbol(name=ID, type="integer", scope=self.cur_scope)
            #     if not self.VarTable.define(varSym):
            #         self.__parseError("This language does not support dynamic typing. "+ID+" has been defined else where with a different type")
            #         return False
            #     else:
            #         return True
            # else:
            #     return success
        # assign for string
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "str":
            ID, success = self.__parseAssign_Stropt()
            if success:
                varSym = VarSymbol(name=ID, type="string", scope=self.cur_scope)
                exist_info = self.FunctionTable.findExistingInstance(varSym)
                if exist_info == -3:
                    self.__parseError("Could not find the scope "+ID+" is in or a parent Scope")
                    return False
                elif exist_info == -2:
                    self.__parseError("Could not find the Variable table to define "+ID+" in")
                    return False
                elif exist_info == -1:
                    self.__parseError("This language does not support Dynamic typing, "+ID+" has been defined else where with a different type")
                    return False
                elif exist_info == 1:
                    # the ID has been defined already same type
                    return True
                elif exist_info == 2:
                    # The ID has not been defined already
                    table_out = self.FunctionTable.lookupByScope(varSym)

                    table_out[1].define(varSym)
                    return True
                else:
                    self.__parseError("This should not be reached at all")
                    return False
            else:
                return success
            # if success:
            #     varSym = VarSymbol(name=ID, type="string", scope=self.cur_scope)
            #     if not self.VarTable.define(varSym):
            #         self.__parseError("This language does not support dynamic typing. "+ID+" has been defined else where with a different type")
            #         return False
            #     else:
            #         return True
            # else:
            #     return success
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "if":
            return self.__parseIf()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "while":
            return self.__parseWhile()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "for":
            return self.__parseFor()
        elif self.nextToken[0] == Tok.KEYWORD and self.nextToken[1] == "def":
            if self.cur_scope == "globe/main":
                return self.__parseFunction_Def()
            else:
                self.__parseError("Not allowed to define a function in another function")
                return False
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
            else:
                print("Invalid Program")