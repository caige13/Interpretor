README FILE
This repository contains:
- test1, test2, test3, test4: Each test file is test source code that can be ran via passing through as cmdline argument.
- StateDiagram.pdf: This is the state diagram for the lexical analyzer
- Lexer.py: Code for the lexical analyzer
- Report.pdf: Contain the Grammar, and semantics for the modified language along with explanations.
- output.txt: contains the output for each test file.

To run the program you pass the source code file as a command line argument such as 
python lexer.py test1.txt 

Feel free to mess around with the source code. The writeability is not friendly and very syntax heavy though.
This repository contains:
- Part1_Documentation: This is a directory that should contain 2 PDFs.
	- Report.pdf: This is the report for Part 1 that contains the static/dynamic semantics along with grammar and state diagram. It also explains changes in part 1 and difficulties I faced in part 1.
	- StateDiagram.pdf: This is just the state diagram for the lexer.
- Part2_Documentation: This is a directory that should contain 1 PDF.
	- Report.pdf: This is the report for Part 2 that contains changes made in part two along with challenges I faced. The updated Grammars are also in this document.
- Source_Code: This is a directory that contains several different source code files for the language. 
	Explanations are given below of each file:
	- test1.txt: A general Program that is a bunch of random code and returns as a valid program.
	- test2.txt: A general Program that is a bunch of random code, but will return a lex error(just to show that the program still implements lexical analysis errors). However if you notice the error thrown is the last line of code showing the previous code before '`' is valid.
	- test3.txt: This file is a bit more advanced. Showing off that the language has scoping(bit fragile explained in report). If you look closely, name1 have a value b that is defined as a integer, but in the main program scope, b is then defined as a string. This is only possible via static scoping because I am not supporting dynamic types. If you also notice there is some decent type checking also. In the main scope 'str b = c+"strange";' is all strings on the right hand side. If you try to put a raw integer, or ID with type integer it will error out. This program also shows off nested for loops, and a function call.
	- test4.txt: Another more general program. Shows off if, else if, and else statements. Will return as a valid program.