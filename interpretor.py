from parse import Parse

class Interpretor():
    def __init__(self, input):
        parser = Parse(input)
        parseResult = parser.parse()
        if parseResult == False:
            exit(0)
        self.cmdList = parser.cmd_list
        self.symbolTable = parser.FunctionTable
        self.scope = ""

    def __execute_print(self, cmd):
        for arg in range(len(cmd)):
            if cmd[arg] == "\n":
                print()
            elif cmd[arg][0] == '"':
                new_string = cmd[arg].replace('"', '')
                print(new_string, end="")
            elif cmd[arg] == '1strCast':
                arg += 1
                print(str(cmd[arg]), end="")

    def __evaluate_strAssign(self, cmd):
        if cmd[0][0] == "[":
            i = 1
            value = []
            while cmd[i] != "]":
                if cmd[i][0] == '"':
                    cmd[i] = cmd[i].replace('"', '')
                elif cmd[i] == "1regID":
                    i += 1

                value.append(cmd[i])
                i += 1
        elif cmd[0][0] == '"':
            value = cmd[0].replace('"', '')





    def interpret_language(self):
        print(self.cmdList)
        for cmd in self.cmdList:
            if cmd[0] == "print":
                self.scope = cmd[1]
                self.__execute_print(cmd[2:])
            if cmd[0] == "strAssign":
                self.scope = cmd[1]
                self.__evaluate_strAssign(cmd[2:])