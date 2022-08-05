import sys
from src import *

code = open(sys.argv[1],'r',encoding='utf-8').read()
#code = open("IOTest.tau",'r',encoding='utf-8').read()
lexer = Lexer(code,tokenTypesList)
lexer.analyse()
parser = Parser(lexer.code_tokens)
rootNode = parser.parseCode()

parser.run(rootNode)