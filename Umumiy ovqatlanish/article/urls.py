from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import ArticleListView, ArticleDetailView, ArticleUpdateView, ArticleDeleteView, ArticleCreateView

urlpatterns = [
    path('article/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('<int:pk>', ArticleDetailView.as_view(), name='article_detail'),
    path('article/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
    path('new/', ArticleCreateView.as_view(), name='article_new'),
    path('', ArticleListView.as_view(), name='article_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)