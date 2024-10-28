from .index_calculator import IndexCalculator


class OrderSplit(IndexCalculator):
    def __init__(self):
        super().__init__(1)
        self.last_md = None

    def calculate(self, new_data):
        if self.last_md is None:
            return {}
        
        
        
        
        
