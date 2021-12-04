import sys
from lexer import Lexer, Tok
from parse import Parse
from interpretor import Interpretor

if len(sys.argv) > 2:
    input_file = sys.argv[2]
    option = sys.argv[1]
else:
    input_file = sys.argv[1]

file = open(input_file, "r")
input = file.read()
file.close()

if option == "p" or option == "parse":
    parser = Parse(input)
    parser.parse()
elif option == "l" or option == "lex":
    lexer = Lexer(input)
    next = lexer.lex()
    while next[0] != Tok.END_OF_INPUT and next[0] != Tok.ERROR:
        print(next)
        next = lexer.lex()
    if next[0] == Tok.ERROR:
        print("ERROR: " + next[1])
else:
    interpretor = Interpretor(input)
    interpretor.interpret_language()