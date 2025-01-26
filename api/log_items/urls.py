from django.urls import path
from log_items import views

urlpatterns = [
    # Already existing:
    path('user/', views.user_data),
    path('user/<str:name>/', views.user_name),
    path('user/<str:name>/update', views.update_user_name),
    path('food_data/', views.user_data, name='food_data_list'),
    
    # NEW: Detail by ID
    path('food_data/<int:food_id>/', views.food_data_detail_by_id, name='food_data_detail_by_id'),
    # NEW: Detail by Name
    path('food_data/name/<str:food_name>/', views.food_data_detail_by_name, name='food_data_detail_by_name'),
    path('food_data/<int:food_id>/', views.food_data_detail_by_id, name='food_data_detail_by_id'),
]
