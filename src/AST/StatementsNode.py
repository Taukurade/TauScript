from .ExpressionNode import ExpressionNode


class StatementsNode(ExpressionNode):
    codeStrs = list()
    
    def addNode(self, node:ExpressionNode):
        self.codeStrs.append(node)