import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from rbt.ic.index_calculator import IndexCalculator


class OlsTrendIC(IndexCalculator):
    def __init__(self, window_size: int = 60):
        super().__init__(window_size)
        self.window_size = window_size
        self.x = np.arange(1, window_size + 1).reshape(-1, 1)
        self.model = LinearRegression()

    def calculate(self, new_data: dict):
        """new_data should be a dict {"time": datetime.datetime, "value": float}

        Args:
            new_data (dict): New data point with time and value.
        """
        # Ensure we have enough data points
        if len(self.data) < self.window_size:
            self.result = {}
            return

        all_data = pd.DataFrame(list(self.data) + [new_data])
        
        # Calculate the time differences in seconds
        last_time = new_data["time"]
        all_data['time_diff'] = (all_data['time'] - last_time).dt.total_seconds()

        # Prepare the X (time differences) and y (values) for regression
        X = all_data[['time_diff']].values.reshape(-1, 1)
        y = all_data[['value']].values.reshape(-1, 1)

        # Fit the OLS model
        self.model.fit(X, y)

        # Calculate the coefficient (slope of the trend) and intercept
        coefficient = self.model.coef_[0][0]
        intercept = self.model.intercept_[0]

        # Calculate the Mean Squared Error (MSE)
        predictions = self.model.predict(X)
        mse = mean_squared_error(y, predictions)
        r_squared = r2_score(y, predictions)

        # Update the result
        self.result = {
            "coefficient": coefficient,
            "intercept": intercept,
            "r_squared": r_squared,
            "mse": mse,
            "window_size": self.window_size,
        }