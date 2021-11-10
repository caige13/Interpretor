from collections import OrderedDict

class Symbol(object):
    def __init__(self, name, type=None, scope="globe/main"):
        self.name = name
        self.type = type
        self.scope = scope

class VarSymbolTable():
    def __init__(self):
        self.table = {}

    def define(self, symbol):
        print('Define: %s' % symbol)
        symbol_check = self.table.get(symbol.name)
        if symbol_check:
            if symbol_check.type == "undefined":
                # This most likely means its a parameter.
                self.table[symbol.name].type = symbol.type
                return True
            elif symbol_check.type != symbol.type:
                return False
            else:
                return True
            # for varSym in symbol_check:
            #     if varSym.type != symbol.type:
            #         varSym.type = symbol.type
            #         return False
            #     existing_name = varSym.scope.split("/")[-1]
            #     for name in varSym.scope.split("/"):
            #         if name != "globe" and name == existing_name:
            #             break
            # else:
            #     self.table[symbol.name].append(symbol)
        else:
            self.table[symbol.name] = symbol
        return True

    def delteEntry(self, symbol):
        print("deleting variable " +symbol.name)
        symbol_check = self.table.get(symbol.name)
        if symbol_check:
            del self.table[symbol.name]
            # for varSym in symbol_check:
            #     if varSym.scope == symbol.scope:
            #         symbol_check.remove(varSym)
            #         if len(symbol_check) == 0:
            #             del self.table[symbol.name]
            #         return True
            # else:
            #     print("Could not find the variable with same name and scope.")
            #     return False
        else:
            print("Could not find entries for the given symbol: "+symbol.name)
            return False

    # We should do a lookup first then a lookupSameScope
    def lookup(self, symbol):
        print('Var Lookup: %s' % symbol)
        try:
            return self.table.get(symbol.name)
        except:
            return False

    # return True if there exists a pre defined ID with same name as symbol parameter within the same scope.
    # def lookupSameScope(self, symbol):
    #     symbol_check = self.table.get(symbol.name)
    #     if symbol_check:
    #         for varSym in symbol_check:
    #             existing_name = symbol_check.scope.split("/")[-1]
    #             for name in varSym.scope.split("/"):
    #                 if name != "globe" and name == existing_name:
    #                     return True
    #         else:
    #             return False
    #     else:
    #         return False

class LoopSymbol(Symbol):
    def __init__(self, name, scope, step_size=None):
        super().__init__(name=name, scope=scope)
        self.step_size = step_size

class FuncSymbol(Symbol):
    def __init__(self, name, return_type=None, scope="globe"):
        super().__init__(name=name,type=return_type, scope=scope)

class VarSymbol(Symbol):
    def __init__(self, name, type, scope):
        super().__init__(name, type, scope)

    def __str__(self):
        return '<{name}:{type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__

class FunctionSymbolTable():
    def __init__(self):
        funcSymbol = FuncSymbol("main")
        self.table = { "globe":{"main":funcSymbol}, "globe/main":[funcSymbol, VarSymbolTable()] }

    def defineFunction(self, symbol):
        print("Defined "+str(symbol.name))
        self.table[symbol.scope+"/"+symbol.name] = [symbol, VarSymbolTable()]
        self.table["globe"][symbol.name]=symbol

    def defineLoop(self, symbol):
        print("Defined loop "+str(symbol.name))
        self.table[symbol.scope+"/"+symbol.name] = [symbol, VarSymbolTable()]

    def lookupFunction(self, name):
        print("looked up "+name)
        return self.table.get("globe/"+name)

    def lookupSymbol(self, symbol):
        print("looked up with symbol "+symbol.name)
        return self.table.get(symbol.scope+"/"+symbol.name)

    def lookupByScope(self, symbol):
        print("looked up with symbol's scope " + symbol.name)
        return self.table.get(symbol.scope)

    # Given var symbol with self.cur_scope

    def updateType(self, symbol, type):
        funcSymb = self.table.get(symbol.scope+"/"+symbol.name)
        if funcSymb:
            funcSymb[0].type = type
            print("Updated "+str(symbol.name)+"'s return type to "+str(type))
            return True
        else:
            return False

    def deleteEntry(self, symbol):
        delete_me = self.table.get(symbol.scope+"/"+symbol.name)
        if delete_me:
            print("deleting "+symbol.name)
            del delete_me[1]
            del self.table[symbol.scope+"/"+symbol.name]
            del self.table["globe"][symbol.name]
        else:
            print("Did not find the entry to delete: "+symbol.name)

    def getGlobe(self):
        return self.table.get("globe")

    def findExistingInstance(self, symbol):
        scope_split = symbol.scope.split("/")
        func_symbol = FuncSymbol(name=symbol.scope.split("/")[-1], scope=symbol.scope)
        to_define_table = self.lookupByScope(func_symbol)
        if to_define_table:
            for i in range(len(scope_split) - 1, 0, -1):
                element_scope = scope_split[0:i + 1]
                scope = ""
                temp_scope = ""
                for j in range(0, len(element_scope)):
                    if j == len(element_scope) - 1:
                        scope += element_scope[j]
                    else:
                        if j == len(element_scope) - 2:
                            temp_scope += element_scope[j]
                        else:
                            temp_scope += element_scope[j] + "/"
                        scope += element_scope[j] + "/"

                funcSymbol = FuncSymbol(name=element_scope[-1], scope=scope)
                table_out = self.lookupByScope(funcSymbol)
                if table_out:
                    try:
                        found_var = table_out[1].lookup(symbol)
                    except:
                        found_var = False
                    if found_var:
                        if symbol.type == "neutral":
                            return 1
                        elif found_var.type == "undefined":
                            # Most likely means its a parameter
                            table_out[1].define(symbol)
                        elif found_var.type != symbol.type:
                            return -1
                        return 1
                else:
                    print("Could not find the current Scope")
                    return -3
            else:
                return 2
        else:
            print("Could not find the table to define "+symbol.name)
            return -2

class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    __repr__ = __str__

class SymbolTable(object):
    def __init__(self):
        self._symbols = OrderedDict()
        self._init_builtins()

    def _init_builtins(self):
        self.define(BuiltinTypeSymbol('INTEGER'))
        self.define(BuiltinTypeSymbol('REAL'))

    def __str__(self):
        s = 'Symbols: {symbols}'.format(
            symbols=[value for value in self._symbols.values()]
        )
        return s

    __repr__ = __str__

    def define(self, symbol):
        print('Define: %s' % symbol)
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        print('Lookup: %s' % name)
        symbol = self._symbols.get(name)
        # 'symbol' is either an instance of the Symbol class or 'None'
        return symbol