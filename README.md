# My own Programming language
Feel free to mess around with the source code. The writeability is not friendly and very syntax heavy though.

## This repository contains:
- Part1_Documentation: This is a directory that should contain 2 PDFs.
	- Report.pdf: This is the report for Part 1 that contains the static/dynamic semantics along with 
	grammar and state diagram. It also explains changes in part 1 and difficulties I faced in part 1.
	- StateDiagram.pdf: This is just the state diagram for the lexer.
- Part2_Documentation: This is a directory that should contain 1 PDF.
	- Report.pdf: This is the report for Part 2 that contains changes made in part two along with further explanations. The updated Grammars are also in this document.
- Source_Code: This is a directory that contains several different source code files for the language. 

	Explanations are given below of each file:
	- test1.txt: A general Program that is a bunch of random code and returns as a valid program. Shows off 
	integer casting and that it works. The input/get command automatically makes the variable a string. After the interpretor, this will enter a infinite loop in the while loop.
	
	- test2.txt: A general Program that is a bunch of random code, but will return a lex error(just to show 
	that the program still implements lexical analysis errors). However if you notice the error thrown is 
	the last line of code showing the previous code before '`' is valid.
	
	- test3.txt: This file is a bit more advanced. Showing off that the language has scoping(bit fragile 	
	explained in report part 2). If you look closely, name1 have a value b that is defined as a integer, but in the 
	main program scope, b is then defined as a string. This is only possible via static scoping because I am 
	not supporting dynamic types. If you also notice there is some decent type checking also. In the main 
	scope 'str b = c+"strange";' is all strings on the right hand side. If you try to put a raw integer, or 
	ID with type integer it will error out. This program also shows off nested for loops, and a function call.
	After the interpretor part this will return out of bounds error because a = [] but was accessed on line 29.
	
	- test4.txt: Another more general program. Shows off if, else if, and else statements. Will return as a 
	valid program. After the interpretor portion this file shows off a working function call for incrementing.
	
	- test_type_error1.txt: A simple program that shows off some type checking. Line 4 will throw an error 
	because first off, b has already been determined a string within that scope. Secondly, its again being 
	recognized as a string in the assignment statement but is given a integer. Hence, this will error out 
	because of the '2'.
	
	- test_type_error2.txt: here we see that casting b as a string in an assignment statement for an integer 
	will error out. This will return invalid after line 3.
	
	- function_return_type1.txt: Show a successful program with a function and doing a function call to it 
	with the correct return type.
	
	- function_return_type2.txt: Shows an invalid program. function1 returns a integer but a is declared as 
	a string, thus this will return a error at line 8. If you look closely again in function1 a is a integer 
	and in main scope a is a string and didnt throw an error until it tried to call a function with a 
	integer return type.
	
	- output_parser.txt: Shows the program output when run parser version for test1-4 files.
	- output_lexer.txt: shows the program output when run lexer version for test1-4 files.
	
- driver.py: This is the driver program that you would call to begin parsing or lexical analysis. 
## Instructions will be given below.
- lexer.py: Where code is for the lexer. It is in a Lexer class.
- parse.py: Where code is for the parser. it is in a Parse class.
- symbol_table: Where code for the Symbol Tables are. This is really what makes the type checking, scoping, 
and see if an ID has been defined before all possible. All the commented out code is stuff that I am keeping 
because I may expand on the symbol tables for Part 3.
- Grammar.xml: This is a file I used to maintain the grammars. It has better styling than me copy and 
pasting into the report so I included it. I used Visual Studio Code to open/edit it.

## DISCLOSURE: This repository is stored on Github. The repository is private so no one can look it up and 
cheat, but there may be additional files/folders github uses that I might not be aware of. I only used 
Github because I program between two computers so it was a easy way to push and pull changes from one 
computer to another. It also insured that I could always have a version of a working program to turn in.


## INSTRUCTIONS:
There are two different modes that are determined by the input. if a 'l' (lower case L) or 'lexer' command 
arguments are given then it just runs part 1 for the source code and spits out the tokens. If a 'p' or 
'parse' command is given then it runs part 2 and parses the program.

	NOTE: THESE COMMANDS ARE CASE SENSITIVE.

The parser is rather verbose with what it does, and the error messages are not perfect. It likly will spit 
out multiple errors where only 1 error message is the correct one, and the others are kinda just 
generalizations or just wrong. However, all of them will have the same line of code where the error happend 
so you can check the line of code to see what one is true. Generally either the first or last message is 
correct.

## EXAMPLES:

To run the parser do:
python driver.py parse ./Source_Code/test1.txt
OR
python driver.py p ./Source_Code/test1.txt

To run the lexer do:
python driver.py lexer ./Source_Code/test1.txt
OR
python driver.py l ./Source_Code/test1.txt will

Extras:
I used a virtual environment, but had to install no extra libraries so standard python should work.