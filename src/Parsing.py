import re

from .AST import *

class Lexer:
    def __init__(self,code:str,tokenList) -> None:
        self.code = code
        self.pos = 0
        self.tokens = tokenList
        self.code_tokens = list()
    def analyse(self):
        while self.nextToken():
            for p,t in enumerate(self.code_tokens):
                if t.type.name in [self.tokens['space'].name,self.tokens['comment'].name]:
                    self.code_tokens.pop(p)
                
    def nextToken(self):
        if self.pos >= len(self.code):
            return False
        for n,tokenType in self.tokens.items():
            
            result = re.match(f"^{tokenType.regex}",self.code[self.pos:])
            if result and result[0]:
                token = Token(tokenType,result[0],self.pos)
                self.pos += len(result[0])
                self.code_tokens.append(token)
                return True
        raise SyntaxError(f"syntax error on {self.pos}")
class Parser:
    def __init__(self,tokens) -> None:
        self.tokens = tokens
        self.pos = 0
        self.scope = {}

    def match(self,*expected):
        if self.pos < len(self.tokens):
            currentToken = self.tokens[self.pos]
            if currentToken.type.name in [t.name for t in expected]:
                self.pos += 1
                return currentToken
        return None 

    def require(self,*expected):
        token = self.match(*expected)
        if token is None:
            raise SyntaxError(f"{expected[0].name} expected at {self.pos} ")
        return token
    
    def parseVariable(self):
        global tokenTypesList
        number = self.match(tokenTypesList["integer"])
        if number is not None:
            return IntegerNode(number)
        string = self.match(tokenTypesList["string"])
        if string is not None:
            return StringNode(string)
        variable = self.match(tokenTypesList["variable"])
        if variable is not None:
            return VariableNode(variable)
        raise SyntaxError(f"Unexpected at {self.pos}")

    def parseOnlyVariable(self):
        global tokenTypesList
        variable = self.match(tokenTypesList["variable"])
        if variable is not None:
            return VariableNode(variable)
        raise SyntaxError(f"Variable expected at {self.pos}")

    def parseExpression(self):
        global tokenTypesList
        if self.match(tokenTypesList['loop']) is not None:
            LoopNode = self.parseLoop()
            return LoopNode
        if self.match(tokenTypesList["variable"]) is None:
            IONode = self.parseIO()
            return IONode

        self.pos -= 1
        variableNode = self.parseVariable()
        assignOperator = self.match(tokenTypesList["assign"])
        if assignOperator is not None:
            rightFormulaNode = self.parseFormula()
            binaryNode = BinOperatorNode(assignOperator,variableNode,rightFormulaNode)
            return binaryNode
        raise SyntaxError(f"assign operator expected at {self.pos}")

    def parseCondition(self):
        global tokenTypesList
        expected = [
            tokenTypesList["eq"],
            tokenTypesList["gt"],
            tokenTypesList["ge"],
            tokenTypesList["lt"],
            tokenTypesList["le"]
        ]
        leftNode = self.parseParenthesesCondition()
        operator = self.match(*expected)
        while operator is not None:
            rightNode = self.parseParenthesesCondition()
            leftNode = BinOperatorNode(operator,leftNode,rightNode)
            operator = self.match(*expected)
        return leftNode
        
    def parseArgs(self):
        global tokenTypesList
        variable = self.parseVariable()
        self.require(tokenTypesList["semicolon"])
        condition = self.parseCondition()
        
        return condition

    def parseLoop(self):
        global tokenTypesList
        if self.match(tokenTypesList["lpar"]) is not None:
            condition = self.parseArgs()
            self.require(tokenTypesList["rpar"])
            self.require(tokenTypesList["blocko"])

                
            self.require(tokenTypesList["blockc"])

    def parseParenthesesCondition(self):
        global tokenTypesList
        if self.match(tokenTypesList["lpar"]) is not None:
            node = self.parseCondition()
            self.require(tokenTypesList["rpar"])
            return node
        else:
            return self.parseVariable()

    def parseParentheses(self):
        global tokenTypesList
        if self.match(tokenTypesList["lpar"]) is not None:
            node = self.parseFormula()
            self.require(tokenTypesList["rpar"])
            return node
        else:
            return self.parseVariable()

    def parseFormula(self):
        global tokenTypesList
        expected = [
            tokenTypesList["sub"],
            tokenTypesList["sum"],
            tokenTypesList["div"],
            tokenTypesList["mult"],
            tokenTypesList["exp"]
        ]
        leftNode = self.parseParentheses()
        operator = self.match(*expected)
        while operator is not None:
            rightNode = self.parseParentheses()
            leftNode = BinOperatorNode(operator,leftNode,rightNode)
            operator = self.match(*expected)
        return leftNode
    
    def parseIO(self):
        global tokenTypesList
        operatorIO = self.match(tokenTypesList["stdout"],tokenTypesList["stdin"])
        if operatorIO.type.name == "stdout":
            return UnarOperatorNode(operatorIO, self.parseFormula())
        elif operatorIO.type.name == "stdin":
            return UnarOperatorNode(operatorIO, self.parseOnlyVariable())
        raise SyntaxError(f"stdout/stdin expected at {self.pos}")
    


    def parseCode(self):
        global tokenTypesList
        root = StatementsNode()
        while self.pos < len(self.tokens):
            codeStringNode = self.parseExpression()
            self.require(tokenTypesList["semicolon"])
            root.addNode(codeStringNode)
        return root
    
    def run(self,node):
        global tokenTypesList
        
        if isinstance(node,IntegerNode):
            return int(node.number.text)
        if isinstance(node, StringNode):
            return str(node.string.text.strip('"'))
        if isinstance(node,UnarOperatorNode):
            self.token_stdout = tokenTypesList['stdout'].name
            self.token_stdin = tokenTypesList["stdin"].name
            match node.operator.type.name:
                case self.token_stdout:
                    print(self.run(node.operand),end='')
                case self.token_stdin:
                    self.scope[node.operand.variable.text] = input()
                    self.run(node.operand)


            

        if isinstance(node, BinOperatorNode):
            self.token_sum = tokenTypesList['sum'].name
            self.token_sub = tokenTypesList['sub'].name
            self.token_mult = tokenTypesList['mult'].name
            self.token_div = tokenTypesList['div'].name
            self.token_exp = tokenTypesList['exp'].name
            self.token_assign = tokenTypesList['assign'].name

            self.token_eq = tokenTypesList['eq'].name
            self.token_gt = tokenTypesList['gt'].name
            self.token_ge = tokenTypesList['ge'].name
            self.token_lt = tokenTypesList['lt'].name
            self.token_le = tokenTypesList['le'].name
            

            match node.operator.type.name:
                case self.token_sum:
                    return self.run(node.leftNode) + self.run(node.rightNode)
                case self.token_sub:
                    return self.run(node.leftNode) - self.run(node.rightNode)
                case self.token_mult:
                    return self.run(node.leftNode) * self.run(node.rightNode)
                case self.token_div:
                    return self.run(node.leftNode) / self.run(node.rightNode)
                case self.token_exp:
                    return self.run(node.leftNode) ** self.run(node.rightNode)

                case self.token_eq:
                    return self.run(node.leftNode) == self.run(node.rightNode)
                case self.token_gt:
                    return self.run(node.leftNode) > self.run(node.rightNode)
                case self.token_ge:
                    return self.run(node.leftNode) >= self.run(node.rightNode)
                case self.token_lt:
                    return self.run(node.leftNode) < self.run(node.rightNode)
                case self.token_le:
                    return self.run(node.leftNode) <= self.run(node.rightNode)
                
                case self.token_assign:
                    result = self.run(node.rightNode)
                    variableNode = node.leftNode
                    self.scope[variableNode.variable.text] = result
                    return result
        if isinstance(node,VariableNode):
            if self.scope.get(node.variable.text) is not None:
                return self.scope[node.variable.text]
            else:
                raise SyntaxError(f"Variable {node.variable.text} not defined")

        if isinstance(node, StatementsNode):
            [self.run(cstr) for cstr in node.codeStrs]
            return
        
class TokenType:
    def __init__(self,name:str,regex):
        self.name = name
        self.regex = regex


class Token:
    def __init__(self,type:TokenType,text:str,position:tuple[int,int]):
        self.type = type
        self.text = text
        self.pos = position



tokenTypesList ={
    "variable":TokenType("variable","#[a-zA-Zа-яА-Я]*"),
    "integer": TokenType("integer", "[0-9]*"),
    "string": TokenType("string",'".*"'),
    "assign": TokenType("assign","="),

    "stdout": TokenType("stdout","stdout"),
    "stdin": TokenType("stdin","stdin"),

    "space": TokenType("space","[ \\n\\t\\r]"),

    "comment": TokenType("space","%.*%"),
    
    "sum": TokenType("sum","[+]"),
    "sub": TokenType("sub","-"),
    "mult": TokenType("mult","[*]"),
    "div": TokenType("div","/"),
    "exp": TokenType("exp","[\^]"),

    "eq": TokenType("eq","=="),
    "gt": TokenType("gt",">"),
    "lt": TokenType("lt","<"),
    "ge": TokenType("ge",">="),
    "le": TokenType("le","<="),
    

    "semicolon": TokenType("semicolon",";"),
    "lpar": TokenType("lpar","\\("),
    "rpar": TokenType("rpar","\\)"),
    "loop": TokenType("loop","loop"),
    "blocko":TokenType("blocko","\\{"),
    "blockc":TokenType("bloclc","\\}")
}


