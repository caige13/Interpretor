from collections import OrderedDict

class VarSymbolTable():
    def __init__(self):
        self.table = {}

    def define(self, symbol):
        print('Define: %s' % symbol)
        self._symbols[symbol.name] = symbol

    def lookup_scope(self, scope):
        print('Lookup: %s' % scope)
        symbol = self._symbols.get(scope)
        # 'symbol' is either an instance of the Symbol class or 'None'
        return symbol

class FunctionSymbolTable():
    def __init__(self):
        self.table = {}

    def define(self, symbol):
        print('Define: %s' % symbol)
        self._symbols[symbol.scope] = symbol

    def lookup(self, name):
        print('Lookup: %s' % name)
        symbol = self._symbols.get(name)
        # 'symbol' is either an instance of the Symbol class or 'None'
        return symbol

class Symbol(object):
    def __init__(self, name, type=None, scope="globe"):
        self.name = name
        self.type = type
        self.scope = scope

class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    __repr__ = __str__

class VarSymbol(Symbol):
    def __init__(self, name, type, scope):
        super().__init__(name, type, scope)

    def __str__(self):
        return '<{name}:{type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__

class FuncSymbol(Symbol):
    def __init__(self,):

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