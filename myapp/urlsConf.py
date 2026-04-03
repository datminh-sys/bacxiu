from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),

    # Quản lý sản phẩm (Đã đồng bộ tên hàm)
    path('products/', views.list_products, name='list_products'),
    path('add_product/', views.add_product, name='add_product'),
    path('list_products/', views.list_products, name='list_products'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('new_product/', views.add_product, name='new_product'), # Trỏ về add_product luôn

    # Tài khoản
    path('register/', views.register, name='register'), # Đảm bảo views.py có hàm này
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboard & Cloud
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/game-data/', views.game_data_api, name='game_data_api'),
    path('cloud/', views.cloud_index, name='cloud_index'),
    path('cloud/upload/', views.upload_file, name='upload_file'),
]
