from django.urls import path
from . import views
# from . import model_views  # Temporairement désactivé pour test

app_name = 'detector'

urlpatterns = [
    # Routes principales
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('about/', views.about, name='about'),
    
    # Routes de gestion des modèles - TEMPORAIREMENT DÉSACTIVÉES
    # path('models/', model_views.models_list, name='models_list'),
    # path('models/switch/', model_views.switch_model, name='switch_model'),
    # path('models/compare/', model_views.compare_models, name='compare_models'),
    # path('models/stats/', model_views.model_stats, name='model_stats'),
    # path('models/save-stats/', model_views.save_model_stats_pickle, name='save_model_stats_pickle'),
    # path('predict-with-model/', model_views.predict_with_model, name='predict_with_model'),
]
