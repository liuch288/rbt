import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from rbt.ic.index_calculator import IndexCalculator


class OlsTrendIC(IndexCalculator):
    def __init__(self, window_size: int = 60, order:int=1):
        super().__init__(window_size)
        self.window_size = window_size
        self.x = np.arange(1, window_size + 1).reshape(-1, 1)
        self.model = LinearRegression()
        if order == 1:
            self.calculate = self.calculate_1
        elif order == 0:
            self.calculate = self.calculate_0

    def calculate_0(self, new_data: dict):
        """修改这个函数，进行只有截距项而没有x的回归，返回值中coefficient固定为None
        """
        # Ensure we have enough data points
        if len(self.data) < self.window_size:
            self.result = {}
            return

        all_data = pd.DataFrame(list(self.data) + [new_data])
        
        # Calculate the mean of y
        y = all_data[['value']].values
        intercept = np.mean(y)

        # Calculate the Mean Squared Error (MSE)
        mse = np.mean((y - intercept) ** 2)

        # Calculate the R-squared (R^2)
        y_mean = np.mean(y)
        r_squared = 1 - (np.sum((y - intercept) ** 2) / np.sum((y - y_mean) ** 2))

        # Update the result
        self.result = {
            "coefficient": None,  # No coefficient as we are not using any x variable
            "intercept": intercept,
            "r_squared": r_squared,
            "mse": mse,
            "window_size": self.window_size,
        }


    def calculate_1(self, new_data: dict):
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