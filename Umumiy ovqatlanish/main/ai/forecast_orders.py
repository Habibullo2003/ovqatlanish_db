# main/management/commands/forecast_orders.py
from django.core.management.base import BaseCommand
from main.models import Buyurtma
import csv
import pandas as pd
from datetime import datetime, timedelta
import random
from main.ai.forecast import run_forecast  # run_forecast ni import qilamiz


class Command(BaseCommand):
    help = 'Buyurtmalarni CSV faylga eksport qiladi, yangi kunlarni qo‘shadi va bashorat qiladi'

    def handle(self, *args, **kwargs):
        csv_file = 'orders.csv'

        # 1) Buyurtmalarni CSV faylga eksport qilish
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['order_id', 'order_date', 'order_amount'])
            for i, order in enumerate(Buyurtma.objects.all().order_by('created_at'), 1):
                writer.writerow([i, order.created_at.date(), order.total_price])
        self.stdout.write(self.style.SUCCESS("Buyurtmalar muvaffaqiyatli eksport qilindi!"))

        # 2) CSV faylni o'qish va yangi sanalarni qo'shish
        df = pd.read_csv(csv_file)

        # Joriy sanani olish va oxirgi sanani aniqlash
        current_date = datetime.now().date()
        if not df.empty:
            last_date = pd.to_datetime(df['order_date'].iloc[-1]).date()
        else:
            last_date = current_date - timedelta(days=1)

        # Yangi sanalarni qo'shish
        new_rows = []
        next_id = df['order_id'].max() + 1 if not df.empty else 1

        while last_date < current_date:
            last_date += timedelta(days=1)
            order_amount = random.randint(10000, 20000)
            new_rows.append({
                'order_id': next_id,
                'order_date': last_date.strftime('%Y-%m-%d'),
                'order_amount': order_amount
            })
            next_id += 1

        # Yangi qatorlarni DataFrame'ga qo'shish va faylga saqlash
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(csv_file, index=False)
            self.stdout.write(self.style.SUCCESS("Yangi sanalar muvaffaqiyatli qo'shildi!"))

        # 3) Buyurtmalarni bashorat qilish
        try:
            forecast_result = run_forecast(csv_path=csv_file, days_ahead=7)
            self.stdout.write(self.style.SUCCESS("Buyurtmalar bashorati muvaffaqiyatli amalga oshirildi!"))

            # Bashorat natijalarini chiqarish
            self.stdout.write("7 kunlik buyurtmalar bashorati:")
            for index, row in forecast_result.iterrows():
                self.stdout.write(
                    f"Sana: {row['ds'].date()}, Bashorat: {int(row['yhat'])} so'm "
                    f"(Oraliq: {int(row['yhat_lower'])} - {int(row['yhat_upper'])} so'm)"
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Bashorat qilishda xatolik: {str(e)}"))
