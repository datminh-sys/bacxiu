import json, os
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import Product


# ====== 2. TRANG CHÍNH ======
def home(request):
    return render(request, 'home.html')



# ====== 4. TÀI KHOẢN (ĐÃ THÊM REGISTER) ======
def register(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        if User.objects.filter(username=u).exists():
            messages.error(request, 'Tên tài khoản đã tồn tại!')
        else:
            User.objects.create_user(username=u, password=p)
            messages.success(request, 'Tạo tài khoản thành công!')
            return redirect('login')
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Sai tài khoản hoặc mật khẩu!')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')


def products(request):
    # Lấy toàn bộ sản phẩm từ database
    all_products = Product.objects.all() 
    # Truyền danh sách sản phẩm vào file HTML (ví dụ: products.html)
    return render(request, 'products.html', {'products': all_products})
# Thêm tiếp đoạn này vào dưới cùng file myapp/views.py
def add_product(request):
    if request.method == 'POST':
        # Logic xử lý thêm sản phẩm của bạn ở đây
        pass
    return render(request, 'add_product.html')



@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

