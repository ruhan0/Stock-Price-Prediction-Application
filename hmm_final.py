import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
import matplotlib.pyplot as plt
from datetime import timedelta

def HMM_model(file: pd.DataFrame):
    df = file
    # Load stock data
    # Replace 'path_to_stock_data.csv' with your actual CSV file path
    # df = pd.read_csv(r'Apple.csv')  # Use a raw string to handle backslashes
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
    df.dropna(inplace=True)  # Drop NaN values
    data = df['log_return'].values.reshape(-1, 1)

    n_components = 2
    model = GaussianHMM(n_components=n_components, covariance_type='full', n_iter=3000)


    model.fit(data)
    hidden_states = model.predict(data)
    df['hidden_state'] = hidden_states
    df['predicted_log_return'] = model.means_[hidden_states].flatten()
    df['predicted_price'] = df['Close'].shift(1) * np.exp(df['predicted_log_return'])
    df.dropna(inplace=True)
    data = df['log_return'].values.reshape(-1, 1)
    hidden_states = model.predict(data)
    df['hidden_state'] = hidden_states
    last_date = df.index[-1]
    last_close_price = df['Close'].iloc[-1]
    n_future_days = (pd.to_datetime('2024-07-15') - last_date).days
    future_dates = [last_date + timedelta(days=i) for i in range(1, n_future_days + 1)]
    future_prices = []
    current_price = last_close_price
    current_state = hidden_states[-1]
    for i in range(n_future_days):
        next_state = model.predict(current_state.reshape(1, -1))[0]
        next_log_return = model.means_[next_state][0]
        next_price = current_price * np.exp(next_log_return)
        future_prices.append(next_price)
        current_price = next_price
        current_state = np.array([next_state])
    future_df = pd.DataFrame({'Date': future_dates, 'Future_Price': future_prices})
    future_df['Future_Price'] = future_df['Future_Price']
    future_df.set_index('Date', inplace=True)
    combined_df = pd.concat([df[['Close']], future_df], axis=1)
    # plt.figure(figsize=(15, 8))
    # plt.plot(df.index, df['Close'], label='Actual Price')
    # #plt.plot(df.index, df['predicted_price'], label='Predicted Price', linestyle='--')
    # plt.plot(future_df.index, future_df['Future_Price'], label='Future Predicted Price', linestyle='-', color='red')
    # plt.legend()
    # plt.title('Actual vs Predicted Stock Prices with Future Predictions')
    # plt.xlabel('Date')
    # plt.ylabel('Price')
    # plt.show()
    return df, future_df
