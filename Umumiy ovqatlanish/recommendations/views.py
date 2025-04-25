from django.views import View
from django.shortcuts import render
from django.contrib.auth import get_user_model
from main.models import UserMenuChoice, Taomlar
import pandas as pd
from sklearn.neighbors import NearestNeighbors

User = get_user_model()

class RecommendationView(View):
    template_name = 'recommendations/menu_recommendation.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, self.template_name, {'error': 'Tizimga kiring.'})

        recommended = self.get_recommendations(request.user)
        if not recommended:
            return render(request, self.template_name, {'error': 'Yetarli maʼlumot yoʻq.'})

        # Barcha taomlarni olish
        all_menus = Taomlar.objects.all()

        return render(request, self.template_name, {
            'recommended_menus': recommended,
            'all_menus': all_menus
        })

    def post(self, request):
        min_p = request.POST.get('min_price')
        max_p = request.POST.get('max_price')

        recommended = self.get_recommendations(request.user)
        if not recommended:
            return render(request, self.template_name, {'error': 'Yetarli maʼlumot yoʻq.'})

        # Barcha taomlarni olish
        all_menus = Taomlar.objects.all()

        # Filtrlangan taomlar (barcha taomlar ichidan narx oralig'iga mos keladiganlarni olish)
        filtered_menus = self.filter_menus(Taomlar.objects.all(), min_p, max_p)

        return render(request, self.template_name, {
            'recommended_menus': recommended,
            'filtered_menus': filtered_menus,  # Filtrlangan taomlar
            'all_menus': all_menus,
            'filtered': True,
            'min_price': min_p,
            'max_price': max_p
        })

    def get_recommendations(self, user):
        rating_matrix, df = self.get_user_rating_matrix()
        if rating_matrix is None or df.empty:
            return None

        user_id = str(user.pk)
        if user_id not in rating_matrix.index:
            return None

        neighbors = self.get_similar_users(rating_matrix, user_id)
        if not neighbors:
            return None

        top_ids = self.get_top_recommendations(df, neighbors)
        return Taomlar.objects.filter(pk__in=top_ids)

    def get_user_rating_matrix(self):
        qs = UserMenuChoice.objects.select_related('menu')
        if not qs.exists():
            return None, None

        data = {'user_id': [], 'menu_id': [], 'rating': []}
        for c in qs:
            data['user_id'].append(str(c.user_id))
            data['menu_id'].append(str(c.menu_id))
            data['rating'].append(c.rating)

        df = pd.DataFrame(data)
        matrix = df.pivot_table(index='user_id', columns='menu_id', values='rating').fillna(0)
        return matrix, df

    def get_similar_users(self, matrix, user_id, n=6):
        model = NearestNeighbors(metric='cosine', algorithm='brute')
        model.fit(matrix)

        max_n = min(n, matrix.shape[0])
        if max_n <= 1:
            return []

        dists, idxs = model.kneighbors([matrix.loc[user_id]], n_neighbors=max_n)
        return [matrix.index[i] for i in idxs.flatten() if matrix.index[i] != user_id]

    def get_top_recommendations(self, df, neighbors, top_n=5):
        sim = df[df['user_id'].isin(neighbors)]
        top = (
            sim[sim['rating'] >= 4]
            .groupby('menu_id')['rating']
            .mean()
            .sort_values(ascending=False)
            .head(top_n)
            .index
            .tolist()
        )
        return top

    def filter_menus(self, qs, min_p, max_p):
        if not min_p and not max_p:
            return qs

        min_value = None
        max_value = None

        if min_p:
            try:
                min_value = float(min_p)
                if min_value < 0:
                    min_value = 0
            except (ValueError, TypeError):
                min_value = None

        if max_p:
            try:
                max_value = float(max_p)
                if max_value < 0:
                    max_value = 0
            except (ValueError, TypeError):
                max_value = None

        if min_value is not None and max_value is not None:
            if min_value > max_value:
                min_value, max_value = max_value, min_value
            return qs.filter(narx__gte=min_value, narx__lte=max_value)

        if min_value is not None:
            return qs.filter(narx__gte=min_value)

        if max_value is not None:
            return qs.filter(narx__lte=max_value)

        return qs