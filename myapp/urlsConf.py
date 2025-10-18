from django.urls import path
from . import views

urlpatterns = [
    # Trang chính
    path('', views.home, name='home'),
    path('home', views.home, name='home'),

    # Quản lý sản phẩm
    path('products', views.show_products, name='products'),
    path('add_product', views.add_product, name='add_product'),
    path('list_products', views.list_products, name='list_products'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('new_product', views.new_product, name='new_product'),

    # Tài khoản
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Game / Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/game-data/', views.game_data_api, name='game_data_api'),
]
