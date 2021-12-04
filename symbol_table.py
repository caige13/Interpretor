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
        self.table[symbol.name] = symbol

    def lookup(self, name):
        print('Var Lookup: %s' % name)
        return self.table.get(name)

class FuncSymbol(Symbol):
    def __init__(self, name, return_type=None, scope="globe", body=None):
        self.body = body
        super().__init__(name=name,type=return_type, scope=scope)

class VarSymbol(Symbol):
    def __init__(self, name, type, scope, value=None):
        self.value = value
        super().__init__(name, type, scope)

    def __str__(self):
        return '<{name}:{type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__

class FunctionSymbolTable():
    def __init__(self):
        funcSymbol = FuncSymbol("main")
        self.table = { "globe":{"main":funcSymbol}, "globe/main":[funcSymbol, VarSymbolTable] }

    def defineFunction(self, symbol):
        print("Defined "+str(symbol.name))
        self.table[symbol.scope+"/"+symbol.name] = [symbol, VarSymbolTable]
        self.table["globe"][symbol.name]=symbol

    def defineLoop(self, symbol):
        print("Defined loop "+str(symbol.name))
        self.table[symbol.scope+"/"+symbol.name] = [symbol, VarSymbolTable]

    def lookupFunction(self, name):
        print("looked up "+name)
        return self.table.get("globe/"+name)

    def updateType(self, symbol, type):
        funcSymb = self.table.get(symbol.scope+"/"+symbol.name)
        if funcSymb:
            funcSymb.type = type
            return True
        else:
            return False

    def getGlobe(self):
        return self.table.get("globe")

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