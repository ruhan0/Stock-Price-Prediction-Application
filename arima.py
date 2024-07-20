import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from scipy.signal import argrelextrema
from typing import Optional




def arima_nodel(file:pd.DataFrame, order_param):
    df = file
    df.set_index('Date')
    data = df['Close']
    train_size = int(len(data) * 0.95)
    train, test = data[:train_size+1], data[train_size:]
    model = ARIMA(train, order=order_param)
    fitted_model = model.fit()
    predictions = fitted_model.forecast(steps=len(test))

    return train, test, predictions




def analyze_trend(data):
    slope, _ = np.polyfit(range(len(data)), data, 1)
    if slope > 0:
        return True
    elif slope < 0:
        return False
