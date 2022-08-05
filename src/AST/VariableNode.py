from .ExpressionNode import ExpressionNode


class VariableNode(ExpressionNode):
    def __init__(self,variable) -> None:
        self.variable = variable