# main/ai/forecast.py
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import os


def run_forecast(csv_path="orders.csv", days_ahead=7):
    """
    CSV fayldan ma'lumotlarni o'qib, buyurtmalarni bashorat qiladi va grafikni saqlaydi.

    Args:
        csv_path (str): CSV fayl manzili (default: "orders.csv")
        days_ahead (int): Bashorat qilinadigan kunlar soni (default: 7)

    Returns:
        DataFrame: Bashorat natijalari ('ds', 'yhat', 'yhat_lower', 'yhat_upper' ustunlari)
    """
    if not os.path.exists(csv_path):
        raise ValueError(f"Fayl topilmadi: {csv_path}")

    # 1) CSV ni o'qib olamiz
    df = pd.read_csv(csv_path)

    # 2) Kerakli ustun nomlarini aniqlaymiz
    # 'ds' (sana) ustunini yaratish
    if 'ds' not in df.columns:
        if 'order_date' in df.columns:
            df['ds'] = pd.to_datetime(df['order_date'])
        elif 'date' in df.columns:
            df['ds'] = pd.to_datetime(df['date'])
        else:
            raise ValueError(
                'DataFrame must have a date column named "ds", "order_date", or "date".'
            )

    # 'y' (qiymat) ustunini yaratish
    if 'y' not in df.columns:
        if 'order_amount' in df.columns:
            df['y'] = df['order_amount']
        elif 'total_amount' in df.columns:
            df['y'] = df['total_amount']
        else:
            raise ValueError(
                'DataFrame must have a value column named "y", "order_amount", or "total_amount".'
            )

    # 3) Faqat kerakli ustunlarni qoldiramiz
    df = df[['ds', 'y']].dropna()
    if df.empty:
        raise ValueError('DataFrame contains no data in "ds" and "y" columns.')

    # 4) Prophet modeli bilan bashorat qilamiz
    model = Prophet(daily_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=days_ahead)
    forecast = model.predict(future)

    # 5) Grafikni saqlaymiz
    os.makedirs('media', exist_ok=True)
    fig = model.plot(forecast)
    plt.title("Buyurtmalar Bashorati (7 kun)")
    fig.savefig("media/forecast.png")
    plt.close(fig)

    # 6) Natijani qaytaramiz (so‘nggi days_ahead satrlar)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
