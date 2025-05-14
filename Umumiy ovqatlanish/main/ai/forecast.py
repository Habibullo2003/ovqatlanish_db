# main/ai/forecast.py
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import logging
from main.models import Buyurtma
from datetime import datetime, timedelta
from django.db.models import Sum

logger = logging.getLogger(__name__)


class OrderForecaster:
    def __init__(self):
        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05
        )

    def prepare_data(self, queryset):
        """Buyurtma queryset'ini Prophet uchun tayyorlash"""
        df = pd.DataFrame(list(queryset.values('created_at', 'total_price')))

        if df.empty:
            raise ValueError("Ma'lumotlar topilmadi")

        df['ds'] = pd.to_datetime(df['created_at'])
        df['y'] = df['total_price']

        # Kunlik ma'lumotlarni guruhlash
        daily_df = df.resample('D', on='ds').agg({'y': 'sum'}).reset_index()

        # Extremum qiymatlarni filtrlash
        q_low = daily_df['y'].quantile(0.05)
        q_high = daily_df['y'].quantile(0.95)
        filtered_df = daily_df[(daily_df['y'] > q_low) & (daily_df['y'] < q_high)]

        if len(filtered_df) < 7:
            raise ValueError("Bashorat uchun yetarli ma'lumot yo'q (kamida 7 kunlik ma'lumot kerak)")

        return filtered_df[['ds', 'y']]

    def generate_forecast(self, queryset, periods=7):
        """Bashorat generatsiya qilish"""
        try:
            # 1. Ma'lumotlarni tayyorlash
            df = self.prepare_data(queryset)

            # 2. Modelni o'qitish
            self.model.fit(df)

            # 3. Bashorat qilish
            future = self.model.make_future_dataframe(periods=periods)
            forecast = self.model.predict(future)

            # 4. Grafik va natijalarni qaytarish
            return self._prepare_results(df, forecast, periods)

        except ValueError as e:
            logger.warning(f"Bashorat qilishda xatolik: {str(e)}")
            return {'graphic': None, 'forecast': [], 'last_date': None}
        except Exception as e:
            logger.error(f"Bashorat qilishda xatolik: {str(e)}", exc_info=True)
            raise

    def _prepare_results(self, actual_df, forecast_df, periods):
        """Natijalarni tayyorlash"""
        # Grafikni yaratish
        fig = self.model.plot(forecast_df)
        plt.title('7 Kunlik Buyurtmalar Bashorati', fontsize=14)
        plt.xlabel('Sana')
        plt.ylabel('Buyurtma miqdori (so\'m)')

        # Grafikni base64 ga aylantirish
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()

        # Bashorat natijalarini tayyorlash
        forecast_data = forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
        forecast_list = []
        for _, row in forecast_data.iterrows():
            prediction = int(row['yhat'])
            max_val = int(row['yhat_upper'])

            # Foiz farqni hisoblash
            try:
                diff_percent = round((max_val - prediction) / prediction * 100) if prediction else 0
            except ZeroDivisionError:
                diff_percent = 0

            forecast_list.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'prediction': prediction,
                'min': int(row['yhat_lower']),
                'max': max_val,
                'diff_percent': diff_percent
            })

        # Oxirgi haqiqiy ma'lumot sanasi
        last_date = actual_df['ds'].max().strftime('%Y-%m-%d')

        return {
            'graphic': image_base64,
            'forecast': forecast_list,
            'last_date': last_date
        }


def get_order_forecast(queryset=None, days=7):
    """Tashqi interfeys uchun funksiya"""
    forecaster = OrderForecaster()
    if queryset is None:
        queryset = Buyurtma.objects.filter(status='delivered').order_by('created_at')
    return forecaster.generate_forecast(queryset, periods=days)
