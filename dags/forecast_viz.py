import pandas as pd
import matplotlib.pyplot as plt

# Create a pandas DataFrame from the data
data = {
    "datetime": pd.to_datetime(["2024-02-07 03:00:00.000", "2024-02-07 06:00:00.000", "2024-02-07 09:00:00.000", "2024-02-07 12:00:00.000", "2024-02-07 15:00:00.000", "2024-02-07 18:00:00.000", "2024-02-07 21:00:00.000", "2024-02-08 00:00:00.000", "2024-02-08 03:00:00.000", "2024-02-08 06:00:00.000", "2024-02-08 09:00:00.000", "2024-02-08 12:00:00.000", "2024-02-08 15:00:00.000", "2024-02-08 18:00:00.000", "2024-02-08 21:00:00.000"]),
    "wind": [3, 3.99, 4.28, 3.4, 3.01, 2.74, 2.38, 2.25, 2.29, 3.12, 4.62, 4.87, 2.9, 1.76, 1.8],
    "temperature": [27.12, 28.42, 29.49, 28.67, 27.55, 26.53, 25.87, 26.1, 30.4, 33.38, 33.14, 30.53, 28.7, 27.51, 26.71],
    "humidity": [83, 74, 67, 71, 76, 79, 79, 76, 56, 46, 49, 58, 66, 72, 73],
    "forecast": ['light rain', 'light rain', 'light rain', 'light rain', 'broken clouds','broken clouds','scattered clouds','scattered clouds','scattered clouds','scattered clouds','clear sky','light rain','clear sky','clear sky','clear sky']
}

df = pd.DataFrame(data)

# Set the datetime as the index
df.set_index("datetime", inplace=True)

# Plot the time series for each variable
plt.figure(figsize=(12, 6))
plt.plot(df["wind"], label="Wind Speed (m/s)")
plt.plot(df["temperature"], label="Temperature (°C)")
plt.plot(df["humidity"], label="Humidity (%)")

# Add forecast labels below datetime
forecast_labels = df.index.strftime("%Y-%m-%d\n%H:%M") + "\n" + df["forecast"]
plt.xticks(df.index, forecast_labels, rotation=45)

plt.xlabel("Datetime")
plt.ylabel("Value")
plt.title("Weather Data Time Series")
plt.legend()

plt.tight_layout()
plt.show()
