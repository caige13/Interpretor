from parse import Parse
from symbol_table import VarSymbol, FuncSymbol, LoopSymbol

class Interpretor():
    def __init__(self, input):
        parser = Parse(input, suppress=True)
        print("\t\tPARSER INFORMATION")
        print("-----------------------------------------------------------------------------------")
        parseResult = parser.parse()
        print("-----------------------------------------------------------------------------------")
        if parseResult == False:
            exit(0)
        self.cmdList = parser.cmd_list
        self.symbolTable = parser.FunctionTable
        self.scope = "globe/main"
        self.stack = []
        self.index = 0

    def __handle_array_access(self, cmd, lock=True):
        i = 1
        id = cmd[i]
        i += 1
        if cmd[i] == "1ArrayID" and lock == True:
            val, cmd =  self.__handle_array_access(cmd[i:])
            varSym = VarSymbol(name=id, type="integer", scope=self.scope)
            varSym = self.symbolTable.retrieve_existing_instance(varSym)
            if varSym == -1:
                varSym = VarSymbol(name=id, type="string", scope=self.scope)
                varSym = self.symbolTable.retrieve_existing_instance(varSym)
            value = varSym.value[int(val)]
            return value, cmd
        elif cmd[i] == "1ArrayID" and lock == False:
            return "1NotGood"
        elif cmd[i] == "1intCast":
            i += 1
            val, cmd = self.__eval_intCast(cmd[i:])
            i = 0
        elif cmd[i] == "1regID":
            i += 1
            varSym = VarSymbol(name=cmd[i], type="integer", scope=self.scope)
            varSym = self.symbolTable.retrieve_existing_instance(varSym)
            val = varSym.value
        else:
            val = cmd[i]
        varSym = VarSymbol(name=id, type="integer", scope=self.scope)
        varSym = self.symbolTable.retrieve_existing_instance(varSym)
        if varSym == -1:
            varSym = VarSymbol(name=id, type="string", scope=self.scope)
            varSym = self.symbolTable.retrieve_existing_instance(varSym)

        if int(val) >= len(varSym.value):
            print("Run Time Error: Out of bounds access")
            exit(0)
        value = varSym.value[int(val)]
        i += 1
        return value, cmd[i:]

    def __eval_strCast(self, cmd):
        i = 0
        if cmd[i] == '1regID':
            i += 1
            varSym = VarSymbol(name=cmd[i], type="integer", scope=self.scope)
            varSym = self.symbolTable.retrieve_existing_instance(varSym)
            if varSym == -1:
                varSym = VarSymbol(name=cmd[i], type="string", scope=self.scope)
                varSym = self.symbolTable.retrieve_existing_instance(varSym)
            return str(varSym.value), cmd[i+1:]
        elif cmd[i][0] == '"':
            value = cmd[i].replace('"', '')
            return value, cmd[1:]
        elif cmd[i] == '1ArrayID':
            val, cmd = self.__handle_array_access(cmd[i:])
            return str(val), cmd
        else:
            return str(cmd[i]), cmd[1:]

    def __eval_intCast(self, cmd):
        i = 0
        if cmd[i] == '1regID':
            i += 1
            varSym = VarSymbol(name=cmd[i], type="string", scope=self.scope)
            varSym = self.symbolTable.retrieve_existing_instance(varSym)
            if varSym == -1:
                varSym = VarSymbol(name=cmd[i], type="integer", scope=self.scope)
                varSym = self.symbolTable.retrieve_existing_instance(varSym)
            return int(varSym.value), cmd[i + 1:]
        elif cmd[i] == '1ArrayID':
            val, cmd = self.__handle_array_access(cmd[i:])
            return int(val), cmd
        else:
            return int(cmd[i]), cmd[1:]

    def __execute_print(self, cmd):
        arg = 0
        while arg < len(cmd):
            if cmd[arg] == "\n":
                print()
            elif cmd[arg][0] == '"':
                new_string = cmd[arg].replace('"', '')
                print(new_string, end="")
            elif arg < len(cmd) and cmd[arg] == '1ArrayID':
                val, cmd = self.__handle_array_access(cmd[arg:])
                if len(cmd) == 0:
                    arg = 0
                else:
                    arg = -1
                print(val, end="")
            elif cmd[arg] == '1strCast':
                arg += 1
                value, cmd = self.__eval_strCast(cmd[arg:])
                arg = -1
                print(str(value), end="")
            elif cmd[arg] == '1regID':
                arg += 1
                varSym = VarSymbol(name=cmd[arg], type="string", scope=self.scope)
                varSym = self.symbolTable.retrieve_existing_instance(varSym)
                if varSym == -1:
                    varSym = VarSymbol(name=cmd[arg], type="integer", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                print(varSym.value, end="")
            elif cmd[i] == '1functionID':
                i += 1
                tmp_value, cmd = self.__function_call(cmd[i:])
                i = -1
            arg += 1

    def __function_call(self, cmd):
        functionName = cmd[0]
        self.stack.append(self.index)
        self.stack.append(self.scope)
        i = len(cmd)-1
        end = 0
        begin = False
        functionCount = 0
        while i > 0:
            if cmd[i] == "1endfunctioncall":
                functionCount += 1
                if functionCount > 1:
                    self.stack.append(cmd[i])
                end = i
                begin = True
            elif begin:
                self.stack.append(cmd[i])
            i -= 1
        funcSymb = self.symbolTable.lookupFunction(functionName)
        variableTable = funcSymb[1]
        funcSymb = funcSymb[0]
        for var in funcSymb.param:
            varSym = VarSymbol(name=var, scope=self.scope)
            varSym = variableTable.lookup(varSym)
            value = self.stack.pop()
            if value == '1regID':
                value = self.stack.pop()
                varSymPass = VarSymbol(name=value, type="string", scope=self.scope)
                varSymPass = self.symbolTable.retrieve_existing_instance(varSymPass)
                if varSymPass == -1:
                    varSymPass = VarSymbol(name=value, type="integer", scope=self.scope)
                    varSymPass = self.symbolTable.retrieve_existing_instance(varSymPass)
                value = varSymPass.value
            elif value == '1ArrayID':
                value = self.stack.pop()
                access = self.stack.pop()
                val, cmd = self.__handle_array_access(['1ArrayID',value, access], False)
                idList = []
                while val == "1NotGood":
                    idList.append(value)
                    value = self.stack.pop()
                    access = self.stack.pop()
                    val, cmd = self.__handle_array_access(['1ArrayID', value, access], False)
                while len(idList) > 0:
                    name = idList.pop()
                    varSym = VarSymbol(name=name, type="string", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    if varSym == -1:
                        varSym = VarSymbol(name=name, type="integer", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    val = varSym.value[val]
                value = val
            elif value == '1strCast':
                value = self.stack.pop()
                value = str(value)
                if value == '1regID':
                    name = self.stack.pop()
                    varSym = VarSymbol(name=name, type="integer", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    if varSym == -1:
                        varSym = VarSymbol(name=name, type="string", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    value = str(varSym.value)
                elif value[0] == '"':
                    value = value.replace('"', '')
                elif value == '1ArrayID':
                    value = self.stack.pop()
                    access = self.stack.pop()
                    val, cmd = self.__handle_array_access(['1ArrayID', value, access], False)
                    idList = []
                    while val == "1NotGood":
                        idList.append(value)
                        value = self.stack.pop()
                        access = self.stack.pop()
                        val, cmd = self.__handle_array_access(['1ArrayID', value, access], False)
                    while len(idList) > 0:
                        name = idList.pop()
                        varSym = VarSymbol(name=name, type="string", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        if varSym == -1:
                            varSym = VarSymbol(name=name, type="integer", scope=self.scope)
                            varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        val = varSym.value[val]
                    value = str(val)
            elif value == '1intCast':
                value = self.stack.pop()
                if value == '1regID':
                    i += 1
                    varSym = VarSymbol(name=cmd[i], type="string", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    if varSym == -1:
                        varSym = VarSymbol(name=cmd[i], type="integer", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    value = int(varSym.value)
                elif value == '1ArrayID':
                    value = self.stack.pop()
                    access = self.stack.pop()
                    val, cmd = self.__handle_array_access(['1ArrayID', value, access], False)
                    idList = []
                    while val == "1NotGood":
                        idList.append(value)
                        value = self.stack.pop()
                        access = self.stack.pop()
                        val, cmd = self.__handle_array_access(['1ArrayID', value, access], False)
                    while len(idList) > 0:
                        name = idList.pop()
                        varSym = VarSymbol(name=name, type="string", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        if varSym == -1:
                            varSym = VarSymbol(name=name, type="integer", scope=self.scope)
                            varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        val = varSym.value[val]
                    value = int(val)
                else:
                    value = int(value)
            elif value == '1functionID':
                cmdList = []
                result = ""
                while result != "1endfunctioncall":
                    result = self.stack.pop()
                    cmdList.append(result)
                value, cmd = self.__function_call(cmdList)
            if varSym.type == "undefined":
                if isinstance(value, int):
                    varSym.type = "integer"
                elif isinstance(value, str):
                    varSym.type = "string"
            varSym.value = value
        self.scope = "globe/"+functionName
        self.index = funcSymb.body
        ignore_count = 1
        nestedIfHelp = False
        while self.index < len(self.cmdList):
            if ignore_count > 0:
                if self.cmdList[self.index][0] == "print":
                    self.scope = self.cmdList[self.index][1]
                    self.__execute_print(self.cmdList[self.index][2:])
                elif self.cmdList[self.index][0] == "strAssign":
                    self.scope = self.cmdList[self.index][1]
                    varSym = VarSymbol(name=self.cmdList[self.index][2], type="string", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    varSym.value = self.__evaluate_strAssign(self.cmdList[self.index][3:])
                elif self.cmdList[self.index][0] == "get":
                    self.scope = self.cmdList[self.index][1]
                    self.__evaluate_get(self.cmdList[self.index][2:])
                elif self.cmdList[self.index][0] == "intAssign":
                    self.scope = self.cmdList[self.index][1]
                    varSym = VarSymbol(name=self.cmdList[self.index][2], type="integer", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    varSym.value = self.__evaluate_intAssign(self.cmdList[self.index][3:])
                elif self.cmdList[self.index][0] == "printf":
                    self.scope = self.cmdList[self.index][1]
                    if self.cmdList[self.index][2] == "Single":
                        # Note the printf by default doesn't end a new line at the end in this language
                        print(self.cmdList[self.index][3].replace('"', ''), end="")
                    else:
                        self.__eval_printf(self.cmdList[self.index][2:])
                elif self.cmdList[self.index][0] == "forloop":
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    forSymbol = LoopSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(forSymbol)
                    forSymbol = table_out[0]
                    forSymbol.body = self.index + 1
                    varSym = VarSymbol(name=self.cmdList[self.index][3], type="integer", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    temp_cmd = []
                    i = 4
                    while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "assignend":
                        temp_cmd.append(self.cmdList[self.index][i])
                        i += 1
                    i += 1
                    varSym.value = self.__evaluate_intAssign(temp_cmd)
                    condition = []
                    while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "conditionend":
                        condition.append(self.cmdList[self.index][i])
                        i += 1
                    i += 1
                    step = []
                    while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "1do":
                        step.append(self.cmdList[self.index][i])
                        i += 1
                    passCond = self.__handle_for_loop(condition, step, varSym, forSymbol)
                    if not passCond:
                        ignore_count -= 1
                elif self.cmdList[self.index][0] == "while":
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    whileSymbol = LoopSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(whileSymbol)
                    whileSymbol = table_out[0]
                    whileSymbol.body = self.index + 1
                    passCond = self.__handle_while_loop(self.cmdList[self.index][3:], whileSymbol)
                    if not passCond:
                        ignore_count -= 1
                elif self.cmdList[self.index][0] == "1functionID":
                    val, cmd = self.__function_call(self.cmdList[self.index][1:])
                    if val != 0:
                        print("Run Time Error: Function call returned ", val)
                        exit(0)
                elif self.cmdList[self.index][0] == "if":
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    ifSymbol = FuncSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(ifSymbol)
                    ifSymbol = table_out[0]
                    ifSymbol.body = self.index + 1
                    passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                    ignore_count -= 1
                    if passCond:
                        nestedIfHelp = True
                elif self.cmdList[self.index][0] == "return":
                    if self.cmdList[self.index][1] == "int":
                        val = self.__evaluate_intAssign(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][1] == "str":
                        val = self.__evaluate_strAssign(self.cmdList[self.index][2:])
                    self.scope = self.stack.pop()
                    self.index = self.stack.pop()
                    if end+1 >= len(cmd):
                        return val, []
                    return val, cmd[end+1:]
                elif self.cmdList[self.index][0] == "1funcend":
                    self.scope = self.stack.pop()
                    self.index = self.stack.pop()
                    return 0, []
            elif self.cmdList[self.index][0] == "elseif" and nestedIfHelp == False:
                name = self.cmdList[self.index][1]
                self.scope = self.cmdList[self.index][2]
                ifSymbol = FuncSymbol(name=name, scope=self.scope)
                table_out = self.symbolTable.lookupByScope(ifSymbol)
                ifSymbol = table_out[0]
                ifSymbol.body = self.index + 1
                passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                if passCond:
                    nestedIfHelp = True
            elif self.cmdList[self.index][0] == "else" and nestedIfHelp == False:
                name = self.cmdList[self.index][1]
                self.scope = self.cmdList[self.index][2]
                ifSymbol = FuncSymbol(name=name, scope=self.scope)
                table_out = self.symbolTable.lookupByScope(ifSymbol)
                ifSymbol = table_out[0]
                ifSymbol.body = self.index + 1
                passCond = self.__handle_if(['1'], ifSymbol)
            elif self.cmdList[self.index][0] == "while" or self.cmdList[self.index][0] == "forloop":
                ignore_count -= 1
            elif self.cmdList[self.index][0] == "forend" or self.cmdList[self.index][0] == "whileend" \
                    or self.cmdList[self.index][0] == "ifend":
                if self.cmdList[self.index][0] == "ifend":
                    nestedIfHelp = False
                ignore_count += 1
            self.index += 1

    def __evaluate_strAssign(self, cmd):
        if cmd[0][0] == "[":
            i = 1
            value = []
            while cmd[i] != "]":
                if cmd[i][0] == '"':
                    cmd[i] = cmd[i].replace('"', '')
                elif cmd[i] == "1regID":
                    i += 1
                    varSym = VarSymbol(name=cmd[i], type="string", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    tmp_value = varSym.value
                elif cmd[i] == '1ArrayID':
                    tmp_value, cmd = self.__handle_array_access(cmd[i:])
                    if len(cmd) == 0:
                        i = 0
                    else:
                        i = -1
                elif cmd[i] == '1functionID':
                    i += 1
                    tmp_value, cmd = self.__function_call(cmd[i:])
                    i = -1
                elif i < len(cmd) and cmd[i] == '1strCast':
                    i += 1
                    tmp_value, cmd = self.__eval_strCast(cmd[i:])
                    if len(cmd) == 0:
                        i = 0
                    else:
                        i = -1
                else:
                    tmp_value = cmd[i]
                value.append(tmp_value[i])
                i += 1
            return value
        value = ""
        tmp_value = ""
        i = 0
        while i < len(cmd):
            if cmd[i][0] == '"':
                tmp_value = cmd[0].replace('"', '')
            elif cmd[i] == "1regID":
                i += 1
                varSym = VarSymbol(name=cmd[i], type="string", scope=self.scope)
                varSym = self.symbolTable.retrieve_existing_instance(varSym)
                tmp_value = varSym.value
            elif cmd[i] == '1ArrayID':
                tmp_value, cmd = self.__handle_array_access(cmd[i:])
                if len(cmd) == 0:
                    i = 0
                else:
                    i = -1
            elif cmd[i] == '1functionID':
                i += 1
                tmp_value, cmd = self.__function_call(cmd[i:])
                i = -1
            elif i < len(cmd) and cmd[i] == '1strCast':
                i += 1
                tmp_value, cmd = self.__eval_strCast(cmd[i:])
                if len(cmd) == 0:
                    i = 0
                else:
                    i = -1
            value += str(tmp_value)
            i += 1
        return value

    def __evaluate_get(self, cmd):
        i = 0
        while i < len(cmd):
            varSym = VarSymbol(name=cmd[i], type="string", scope=self.scope)
            varSym = self.symbolTable.retrieve_existing_instance(varSym)
            msg = "input: "
            if i+1 < len(cmd) and cmd[i+1][0] == '"':
                i += 1
                msg = cmd[i]
                msg = msg.replace('"', '')
            val = input(msg)
            varSym.value = val
            i += 1

    def __evaluate_intAssign(self, cmd):
        if cmd[0][0] == "[":
            i = 1
            value = []
            while cmd[i] != "]":
                if cmd[i] == "1regID":
                    i += 1
                    varSym = VarSymbol(name=cmd[i], type="integer", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    tmp_value = varSym.value
                elif cmd[i] == '1ArrayID':
                    tmp_value, cmd = self.__handle_array_access(cmd[i:])
                    if len(cmd) == 0:
                        i = 0
                    else:
                        i = -1
                elif cmd[i] == '1functionID':
                    i += 1
                    tmp_value, cmd = self.__function_call(cmd[i:])
                    i = -1
                elif i < len(cmd) and cmd[i] == '1intCast':
                    i += 1
                    tmp_value, cmd = self.__eval_intCast(cmd[i:])
                    if len(cmd) == 0:
                        i = 0
                    else:
                        i = -1
                else:
                    tmp_value = cmd[i]
                value.append(int(tmp_value))
                i += 1
            return value
        i = 0
        value = ""
        while i < len(cmd):
            if cmd[i] == "1regID":
                i += 1
                if cmd[i] == "-":
                    i += 1
                varSym = VarSymbol(name=cmd[i], type="integer", scope=self.scope)
                varSym = self.symbolTable.retrieve_existing_instance(varSym)
                tmp_value = varSym.value
            elif i < len(cmd) and cmd[i] == '1ArrayID':
                tmp_value, cmd = self.__handle_array_access(cmd[i:])
                if len(cmd) == 0:
                    i = 0
                else:
                    i = -1
            elif cmd[i] == '1functionID':
                i += 1
                tmp_value, cmd = self.__function_call(cmd[i:])
                i = -1
            elif i < len(cmd) and cmd[i] == '1intCast':
                i += 1
                tmp_value, cmd = self.__eval_intCast(cmd[i:])
                if len(cmd) == 0:
                    i = 0
                else:
                    i = -1
            else:
                tmp_value = cmd[i]
            value += str(tmp_value)
            i += 1
        value = eval(value)
        return value

    def __eval_printf(self, cmd):
        mod_string = cmd[0]
        split_string = [""]
        i = 0
        for c in range(len(mod_string)):
            if mod_string[c] == '%':
                i += 1
                split_string.append("")
                split_string[i] = mod_string[c]
            elif mod_string[c-1] == '%':
                split_string[i] +=mod_string[c]
                i +=1
                split_string.append("")
            elif mod_string[c] == '"':
                continue
            elif mod_string[c] == "\\":
                continue
            elif mod_string[c] == "n" and c != 0 and mod_string[c-1] == "\\":
                split_string[i] += "\n"
            elif mod_string[c] == "t" and c != 0 and mod_string[c-1] == "\\":
                split_string[i] += "\t"
            elif mod_string[c] == "r" and c != 0 and mod_string[c-1] == "\\":
                split_string[i] += "\r"
            elif mod_string[c] == '"' and c != 0 and mod_string[c-1] == "\\":
                split_string[i] += "\""
            elif mod_string[c] == "'" and c != 0 and mod_string[c-1] == "\\":
                split_string[i] += "\'"
            else:
                split_string[i] += mod_string[c]

        j = 0
        i = 1
        while j < len(split_string):
            if split_string[j] == '%d' or split_string[j] == '%s':
                if i < len(cmd) and cmd[i] == '1ArrayID':
                    val, cmd = self.__handle_array_access(cmd[i:])
                    if len(cmd) == 0:
                        i = 0
                    else:
                        i = -1
                elif i < len(cmd) and cmd[i] == '1regID':
                        i += 1
                        varSym = VarSymbol(name=cmd[i], type="string", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        if varSym == -1:
                            varSym = VarSymbol(name=cmd[i], type="integer", scope=self.scope)
                            varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        val = varSym.value
                elif i < len(cmd) and cmd[i] == '1strCast':
                    i += 1
                    val, cmd = self.__eval_strCast(cmd[i:])
                    if len(cmd) == 0:
                        i = 0
                    else:
                        i = -1
                elif i < len(cmd) and cmd[i] == '1intCast':
                    i += 1
                    val, cmd = self.__eval_intCast(cmd[i:])
                    if len(cmd) == 0:
                        i = 0
                    else:
                        i = -1
                elif cmd[i] == '1functionID':
                    i += 1
                    val, cmd = self.__function_call(cmd[i:])
                    i = -1
                elif i < len(cmd) and cmd[i][0] == '"':
                    temporary = cmd[i].replace('"', '')
                    val = temporary
                elif i < len(cmd):
                    val = cmd[i]
                i += 1
            else:
                val = split_string[j]
            print(val, end="")
            j += 1

    def __handle_function_definition(self, cmd):
        function_name = cmd[0]
        funcSymbol = self.symbolTable.lookupFunction(function_name)
        self.symbolTable.table["globe"][function_name].body = self.index+1
        funcSymbol[0].body = self.index+1

    def __handle_for_loop(self, this_condition, step_size, control_var, this_forSymbol):
        iteration = 0
        ignore_count = 1
        while(self.__evaluate_intAssign(this_condition)):
            self.index = this_forSymbol.body
            nestedIfHelp = False
            # dont need to check for length because a end is guarenteed by the parser.
            while self.cmdList[self.index][0] != "forend":
                iteration += 1
                if ignore_count > 0:
                    if self.cmdList[self.index][0] == "print":
                        self.scope = self.cmdList[self.index][1]
                        self.__execute_print(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][0] == "strAssign":
                        self.scope = self.cmdList[self.index][1]
                        varSym = VarSymbol(name=self.cmdList[self.index][2], type="string", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        varSym.value = self.__evaluate_strAssign(self.cmdList[self.index][3:])
                    elif self.cmdList[self.index][0] == "get":
                        self.scope = self.cmdList[self.index][1]
                        self.__evaluate_get(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][0] == "intAssign":
                        self.scope = self.cmdList[self.index][1]
                        varSym = VarSymbol(name=self.cmdList[self.index][2], type="integer", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        varSym.value = self.__evaluate_intAssign(self.cmdList[self.index][3:])
                    elif self.cmdList[self.index][0] == "printf":
                        self.scope = self.cmdList[self.index][1]
                        if self.cmdList[self.index][2] == "Single":
                            # Note the printf by default doesn't end a new line at the end in this language
                            print(self.cmdList[self.index][3].replace('"', ''), end="")
                        else:
                            self.__eval_printf(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][0] == "1functionID":
                        val, cmd = self.__function_call(self.cmdList[self.index][1:])
                        if val != 0:
                            print("Run Time Error: Function call returned ", val)
                            exit(0)
                    elif self.cmdList[self.index][0] == "forloop":
                        name = self.cmdList[self.index][1]
                        self.scope = self.cmdList[self.index][2]
                        forSymbol = LoopSymbol(name=name, scope=self.scope)
                        table_out = self.symbolTable.lookupByScope(forSymbol)
                        forSymbol = table_out[0]
                        forSymbol.body = self.index + 1
                        varSym = VarSymbol(name=self.cmdList[self.index][3], type="integer", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        temp_cmd = []
                        i = 4
                        while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "assignend":
                            temp_cmd.append(self.cmdList[self.index][i])
                            i += 1
                        i += 1
                        varSym.value = self.__evaluate_intAssign(temp_cmd)
                        condition = []
                        while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "conditionend":
                            condition.append(self.cmdList[self.index][i])
                            i += 1
                        i += 1
                        step = []
                        while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "1do":
                            step.append(self.cmdList[self.index][i])
                            i += 1
                        passCond = self.__handle_for_loop(condition, step, varSym, forSymbol)
                        if not passCond:
                            ignore_count -= 1
                    elif self.cmdList[self.index][0] == "while":
                        name = self.cmdList[self.index][1]
                        self.scope = self.cmdList[self.index][2]
                        whileSymbol = LoopSymbol(name=name, scope=self.scope)
                        table_out = self.symbolTable.lookupByScope(whileSymbol)
                        whileSymbol = table_out[0]
                        whileSymbol.body = self.index + 1
                        passCond = self.__handle_while_loop(self.cmdList[self.index][3:], whileSymbol)
                        if not passCond:
                            ignore_count -= 1
                    elif self.cmdList[self.index][0] == "if":
                        name = self.cmdList[self.index][1]
                        self.scope = self.cmdList[self.index][2]
                        ifSymbol = FuncSymbol(name=name, scope=self.scope)
                        table_out = self.symbolTable.lookupByScope(ifSymbol)
                        ifSymbol = table_out[0]
                        ifSymbol.body = self.index + 1
                        passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                        ignore_count -= 1
                        if passCond:
                            nestedIfHelp = True
                elif self.cmdList[self.index][0] == "elseif" and nestedIfHelp == False:
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    ifSymbol = FuncSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(ifSymbol)
                    ifSymbol = table_out[0]
                    ifSymbol.body = self.index + 1
                    passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                    if passCond:
                        nestedIfHelp = True
                elif self.cmdList[self.index][0] == "else" and nestedIfHelp == False:
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    ifSymbol = FuncSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(ifSymbol)
                    ifSymbol = table_out[0]
                    ifSymbol.body = self.index + 1
                    passCond = self.__handle_if(['1'], ifSymbol)
                elif self.cmdList[self.index][0] == "while" or self.cmdList[self.index][0] == "forloop":
                    ignore_count -= 1
                elif self.cmdList[self.index][0] == "forend" or self.cmdList[self.index][0] == "whileend" \
                        or self.cmdList[self.index][0] == "ifend":
                    if self.cmdList[self.index][0] == "ifend":
                        nestedIfHelp = False
                    ignore_count += 1
                self.index += 1
            control_var.value = self.__evaluate_intAssign(step_size)
        if iteration > 0:
            return True
        else:
            return False

    def __handle_while_loop(self, this_condition, this_whileSymbol):
        iteration = 0
        ignore_count = 1
        while self.__evaluate_intAssign(this_condition):
            self.index = this_whileSymbol.body
            nestedIfHelp = False
            while self.cmdList[self.index][0] != "whileend":
                if ignore_count > 0:
                    iteration += 1
                    if self.cmdList[self.index][0] == "print":
                        self.scope = self.cmdList[self.index][1]
                        self.__execute_print(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][0] == "strAssign":
                        self.scope = self.cmdList[self.index][1]
                        varSym = VarSymbol(name=self.cmdList[self.index][2], type="string", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        varSym.value = self.__evaluate_strAssign(self.cmdList[self.index][3:])
                    elif self.cmdList[self.index][0] == "get":
                        self.scope = self.cmdList[self.index][1]
                        self.__evaluate_get(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][0] == "intAssign":
                        self.scope = self.cmdList[self.index][1]
                        varSym = VarSymbol(name=self.cmdList[self.index][2], type="integer", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        varSym.value = self.__evaluate_intAssign(self.cmdList[self.index][3:])
                    elif self.cmdList[self.index][0] == "printf":
                        self.scope = self.cmdList[self.index][1]
                        if self.cmdList[self.index][2] == "Single":
                            # Note the printf by default doesn't end a new line at the end in this language
                            print(self.cmdList[self.index][3].replace('"', ''), end="")
                        else:
                            self.__eval_printf(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][0] == "1functionID":
                        val, cmd = self.__function_call(self.cmdList[self.index][1:])
                        if val != 0:
                            print("Run Time Error: Function call returned ", val)
                            exit(0)
                    elif self.cmdList[self.index][0] == "forloop":
                        name = self.cmdList[self.index][1]
                        self.scope = self.cmdList[self.index][2]
                        forSymbol = LoopSymbol(name=name, scope=self.scope)
                        table_out = self.symbolTable.lookupByScope(forSymbol)
                        forSymbol = table_out[0]
                        forSymbol.body = self.index + 1
                        varSym = VarSymbol(name=self.cmdList[self.index][3], type="integer", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        temp_cmd = []
                        i = 4
                        while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "assignend":
                            temp_cmd.append(self.cmdList[self.index][i])
                            i += 1
                        i += 1
                        varSym.value = self.__evaluate_intAssign(temp_cmd)
                        condition = []
                        while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "conditionend":
                            condition.append(self.cmdList[self.index][i])
                            i += 1
                        i += 1
                        step = []
                        while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "1do":
                            step.append(self.cmdList[self.index][i])
                            i += 1
                        passCond = self.__handle_for_loop(condition, step, varSym, forSymbol)
                        if not passCond:
                            ignore_count -= 1
                    elif self.cmdList[self.index][0] == "while":
                        name = self.cmdList[self.index][1]
                        self.scope = self.cmdList[self.index][2]
                        whileSymbol = LoopSymbol(name=name, scope=self.scope)
                        table_out = self.symbolTable.lookupByScope(whileSymbol)
                        whileSymbol = table_out[0]
                        whileSymbol.body = self.index + 1
                        passCond = self.__handle_while_loop(self.cmdList[self.index][3:], whileSymbol)
                        if not passCond:
                            ignore_count -= 1
                    elif self.cmdList[self.index][0] == "if":
                        name = self.cmdList[self.index][1]
                        self.scope = self.cmdList[self.index][2]
                        ifSymbol = FuncSymbol(name=name, scope=self.scope)
                        table_out = self.symbolTable.lookupByScope(ifSymbol)
                        ifSymbol = table_out[0]
                        ifSymbol.body = self.index + 1
                        passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                        ignore_count -= 1
                        if passCond:
                            nestedIfHelp = True
                elif self.cmdList[self.index][0] == "elseif" and nestedIfHelp == False:
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    ifSymbol = FuncSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(ifSymbol)
                    ifSymbol = table_out[0]
                    ifSymbol.body = self.index + 1
                    passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                    if passCond:
                        nestedIfHelp = True
                elif self.cmdList[self.index][0] == "else" and nestedIfHelp == False:
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    ifSymbol = FuncSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(ifSymbol)
                    ifSymbol = table_out[0]
                    ifSymbol.body = self.index + 1
                    passCond = self.__handle_if(['1'], ifSymbol)
                elif self.cmdList[self.index][0] == "while" or self.cmdList[self.index][0] == "forloop":
                    ignore_count -= 1
                elif self.cmdList[self.index][0] == "forend" or self.cmdList[self.index][0] == "whileend" \
                        or self.cmdList[self.index][0] == "ifend":
                    if self.cmdList[self.index][0] == "ifend":
                        nestedIfHelp = False
                    ignore_count += 1
                self.index += 1
        if iteration > 0:
            return True
        else:
            return False

    def __handle_if(self, this_condition, this_ifSymbol):
        passed = False
        if self.__evaluate_intAssign(this_condition):
            passed = True
            ignore_count = 1
            self.index = this_ifSymbol.body
            nestedIfHelp = False
            while self.cmdList[self.index][0] != "ifend" and self.cmdList[self.index][0] != "elseif" \
                    and self.cmdList[self.index][0] != "else":
                if ignore_count > 0:
                    if self.cmdList[self.index][0] == "print":
                        self.scope = self.cmdList[self.index][1]
                        self.__execute_print(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][0] == "strAssign":
                        self.scope = self.cmdList[self.index][1]
                        varSym = VarSymbol(name=self.cmdList[self.index][2], type="string", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        varSym.value = self.__evaluate_strAssign(self.cmdList[self.index][3:])
                    elif self.cmdList[self.index][0] == "get":
                        self.scope = self.cmdList[self.index][1]
                        self.__evaluate_get(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][0] == "intAssign":
                        self.scope = self.cmdList[self.index][1]
                        varSym = VarSymbol(name=self.cmdList[self.index][2], type="integer", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        varSym.value = self.__evaluate_intAssign(self.cmdList[self.index][3:])
                    elif self.cmdList[self.index][0] == "printf":
                        self.scope = self.cmdList[self.index][1]
                        if self.cmdList[self.index][2] == "Single":
                            # Note the printf by default doesn't end a new line at the end in this language
                            print(self.cmdList[self.index][3].replace('"', ''), end="")
                        else:
                            self.__eval_printf(self.cmdList[self.index][2:])
                    elif self.cmdList[self.index][0] == "1functionID":
                        val, cmd = self.__function_call(self.cmdList[self.index][1:])
                        if val != 0:
                            print("Run Time Error: Function call returned ", val)
                            exit(0)
                    elif self.cmdList[self.index][0] == "forloop":
                        name = self.cmdList[self.index][1]
                        self.scope = self.cmdList[self.index][2]
                        forSymbol = LoopSymbol(name=name, scope=self.scope)
                        table_out = self.symbolTable.lookupByScope(forSymbol)
                        forSymbol = table_out[0]
                        forSymbol.body = self.index + 1
                        varSym = VarSymbol(name=self.cmdList[self.index][3], type="integer", scope=self.scope)
                        varSym = self.symbolTable.retrieve_existing_instance(varSym)
                        temp_cmd = []
                        i = 4
                        while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "assignend":
                            temp_cmd.append(self.cmdList[self.index][i])
                            i += 1
                        i += 1
                        varSym.value = self.__evaluate_intAssign(temp_cmd)
                        condition = []
                        while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "conditionend":
                            condition.append(self.cmdList[self.index][i])
                            i += 1
                        i += 1
                        step = []
                        while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "1do":
                            step.append(self.cmdList[self.index][i])
                            i += 1
                        passCond = self.__handle_for_loop(condition, step, varSym, forSymbol)
                        if not passCond:
                            ignore_count -= 1
                    elif self.cmdList[self.index][0] == "while":
                        name = self.cmdList[self.index][1]
                        self.scope = self.cmdList[self.index][2]
                        whileSymbol = LoopSymbol(name=name, scope=self.scope)
                        table_out = self.symbolTable.lookupByScope(whileSymbol)
                        whileSymbol = table_out[0]
                        whileSymbol.body = self.index + 1
                        passCond = self.__handle_while_loop(self.cmdList[self.index][3:], whileSymbol)
                        if not passCond:
                            ignore_count -= 1
                    elif self.cmdList[self.index][0] == "if":
                        name = self.cmdList[self.index][1]
                        self.scope = self.cmdList[self.index][2]
                        ifSymbol = FuncSymbol(name=name, scope=self.scope)
                        table_out = self.symbolTable.lookupByScope(ifSymbol)
                        ifSymbol = table_out[0]
                        ifSymbol.body = self.index + 1
                        passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                        ignore_count -= 1
                        if passCond:
                            nestedIfHelp = True
                elif self.cmdList[self.index][0] == "elseif" and nestedIfHelp == False:
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    ifSymbol = FuncSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(ifSymbol)
                    ifSymbol = table_out[0]
                    ifSymbol.body = self.index + 1
                    passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                    if passCond:
                        nestedIfHelp = True
                elif self.cmdList[self.index][0] == "else" and nestedIfHelp == False:
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    ifSymbol = FuncSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(ifSymbol)
                    ifSymbol = table_out[0]
                    ifSymbol.body = self.index + 1
                    passCond = self.__handle_if(['1'], ifSymbol)
                elif self.cmdList[self.index][0] == "while" or self.cmdList[self.index][0] == "forloop":
                    ignore_count -= 1
                elif self.cmdList[self.index][0] == "forend" or self.cmdList[self.index][0] == "whileend" \
                        or self.cmdList[self.index][0] == "ifend":
                    if self.cmdList[self.index][0] == "ifend":
                        nestedIfHelp = False
                    ignore_count += 1
                self.index += 1
        self.index = this_ifSymbol.body
        if passed:
            return True
        else:
            return False

    def interpret_language(self):
        ignore_count = 1
        nestedIfHelp = False
        while self.index < len(self.cmdList):
            if ignore_count > 0:
                if self.cmdList[self.index][0] == "print":
                    self.scope = self.cmdList[self.index][1]
                    self.__execute_print(self.cmdList[self.index][2:])
                elif self.cmdList[self.index][0] == "strAssign":
                    self.scope = self.cmdList[self.index][1]
                    varSym = VarSymbol(name=self.cmdList[self.index][2], type="string", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    varSym.value = self.__evaluate_strAssign(self.cmdList[self.index][3:])
                elif self.cmdList[self.index][0] == "get":
                    self.scope = self.cmdList[self.index][1]
                    self.__evaluate_get(self.cmdList[self.index][2:])
                elif self.cmdList[self.index][0] == "intAssign":
                    self.scope = self.cmdList[self.index][1]
                    varSym = VarSymbol(name=self.cmdList[self.index][2], type="integer", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    varSym.value = self.__evaluate_intAssign(self.cmdList[self.index][3:])
                elif self.cmdList[self.index][0] == "printf":
                    self.scope = self.cmdList[self.index][1]
                    if self.cmdList[self.index][2] == "Single":
                        # Note the printf by default doesn't end a new line at the end in this language
                        print(self.cmdList[self.index][3].replace('"', ''), end="")
                    else:
                        self.__eval_printf(self.cmdList[self.index][2:])
                elif self.cmdList[self.index][0] == "def":
                    ignore_count -= 1
                    self.__handle_function_definition(self.cmdList[self.index][1:])
                elif self.cmdList[self.index][0] == "1functionID":
                    val, cmd = self.__function_call(self.cmdList[self.index][1:])
                    if val != 0:
                        print("Run Time Error: Function call returned ", val)
                        exit(0)
                elif self.cmdList[self.index][0] == "forloop":
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    forSymbol = LoopSymbol(name=name,scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(forSymbol)
                    forSymbol = table_out[0]
                    forSymbol.body = self.index + 1
                    varSym = VarSymbol(name=self.cmdList[self.index][3], type="integer", scope=self.scope)
                    varSym = self.symbolTable.retrieve_existing_instance(varSym)
                    temp_cmd = []
                    i = 4
                    while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "assignend":
                        temp_cmd.append(self.cmdList[self.index][i])
                        i += 1
                    i += 1
                    varSym.value = self.__evaluate_intAssign(temp_cmd)
                    condition = []
                    while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "conditionend":
                        condition.append(self.cmdList[self.index][i])
                        i += 1
                    i += 1
                    step = []
                    while i < len(self.cmdList[self.index]) and self.cmdList[self.index][i] != "1do":
                        step.append(self.cmdList[self.index][i])
                        i += 1
                    passCond = self.__handle_for_loop(condition, step, varSym, forSymbol)
                    if not passCond:
                        ignore_count -= 1
                elif self.cmdList[self.index][0] == "while":
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    whileSymbol = LoopSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(whileSymbol)
                    whileSymbol = table_out[0]
                    whileSymbol.body = self.index + 1
                    passCond = self.__handle_while_loop(self.cmdList[self.index][3:], whileSymbol)
                    if not passCond:
                        ignore_count -= 1
                elif self.cmdList[self.index][0] == "if":
                    name = self.cmdList[self.index][1]
                    self.scope = self.cmdList[self.index][2]
                    ifSymbol = FuncSymbol(name=name, scope=self.scope)
                    table_out = self.symbolTable.lookupByScope(ifSymbol)
                    ifSymbol = table_out[0]
                    ifSymbol.body = self.index + 1
                    passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                    ignore_count -= 1
                    if passCond:
                        nestedIfHelp = True
            elif self.cmdList[self.index][0] == "elseif" and nestedIfHelp == False:
                name = self.cmdList[self.index][1]
                self.scope = self.cmdList[self.index][2]
                ifSymbol = FuncSymbol(name=name, scope=self.scope)
                table_out = self.symbolTable.lookupByScope(ifSymbol)
                ifSymbol = table_out[0]
                ifSymbol.body = self.index + 1
                passCond = self.__handle_if(self.cmdList[self.index][3:], ifSymbol)
                if passCond:
                    nestedIfHelp = True
            elif self.cmdList[self.index][0] == "else" and nestedIfHelp == False:
                name = self.cmdList[self.index][1]
                self.scope = self.cmdList[self.index][2]
                ifSymbol = FuncSymbol(name=name, scope=self.scope)
                table_out = self.symbolTable.lookupByScope(ifSymbol)
                ifSymbol = table_out[0]
                ifSymbol.body = self.index + 1
                passCond = self.__handle_if(['1'], ifSymbol)
            elif self.cmdList[self.index][0] == "while" or self.cmdList[self.index][0] == "forloop":
                ignore_count -= 1
            elif self.cmdList[self.index][0] == "1funcend" or self.cmdList[self.index][0] == "forend" \
                or self.cmdList[self.index][0] == "whileend" or self.cmdList[self.index][0] == "ifend":
                if self.cmdList[self.index][0] == "ifend":
                    nestedIfHelp = False
                ignore_count += 1
            self.index += 1