import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64


def monitoring(csv_file):
    # CSV faylni o‘qish
    df = pd.read_csv(csv_file)

    # Monitoring uchun xususiyatlar
    xususiyatlar = ['MijozSoni', 'Daromad', 'XizmatTezligi']
    standart = StandardScaler()
    df_standart = standart.fit_transform(df[xususiyatlar])

    # KMeans yordamida restoranlarni klasterlash
    kmeans_model = KMeans(n_clusters=3, random_state=0)
    df['Klaster'] = kmeans_model.fit_predict(df_standart)

    # Grafik yaratish
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df, x='MijozSoni', y='Daromad', hue='Klaster', palette='Set2', s=100)
    plt.title('Restoranlar monitoringi: Mijoz soni vs Daromad')
    plt.xlabel('Mijoz soni (kunlik)')
    plt.ylabel('Daromad (so‘m)')
    plt.grid(True)

    # Grafikni rasmga olish
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return df, image
