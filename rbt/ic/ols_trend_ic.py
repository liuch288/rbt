import numpy as np
from rbt.ic.index_calculator import IndexCalculator
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class OlsTrendIC(IndexCalculator):
    def __init__(self, window_size: int = 60):
        super().__init__(window_size)
        self.window_size = window_size
        self.x = np.arange(1, window_size + 1).reshape(-1, 1)
        self.model = LinearRegression()

    def calculate(self, new_data):
        # Ensure we have enough data points
        if len(self.data) < self.window_size:
            self.result = None
            return

        # Extract the last 'window_size' price data for regression
        y = np.array(self.data).reshape(-1, 1)

        # Fit the OLS model
        self.model.fit(self.x, y)

        # Calculate the coefficient (slope of the trend)
        coefficient = self.model.coef_[0][0]

        # Calculate the Mean Squared Error (MSE)
        predictions = self.model.predict(self.x)
        mse = mean_squared_error(y, predictions)
        r_squared = r2_score(y, predictions)

        # Update the result
        self.result = {
            'coefficient': coefficient,
            'r_squared': r_squared,
            'mse': mse,
            'window_size': self.window_size
        }

    def get_result(self):
        return self.result
