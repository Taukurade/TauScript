
from .ExpressionNode import ExpressionNode


class BinOperatorNode(ExpressionNode):
    def __init__(self,operator, leftNode, rightNode):
        
        self.operator = operator
        self.leftNode = leftNode
        self.rightNode = rightNode
        