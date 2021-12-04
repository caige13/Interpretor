from parse import Parse

class Interpretor():
    def __init__(self, input):
        self.parser = Parse(input)
        self.cmd = self.parser.parse()

    def interpret_language(self):