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
from .models import Product  # Đảm bảo đã import model Product

# ====== DECORATOR WHITE LIST ======
def whitelist_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Admin (Superuser) hoặc người trong whitelist mới được vào
        if request.user.is_superuser or request.user.username in getattr(settings, 'CLOUD_WHITELIST', []):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

# ====== TRANG CHÍNH ======
def home(request):
    return render(request, 'home.html')

# ====== QUẢN LÝ SẢN PHẨM (ĐÃ KHÔI PHỤC ĐẦY ĐỦ) ======
def list_products(request):
    products = Product.objects.all()
    return render(request, 'list_products.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        Product.objects.create(name=name, price=price)
        return redirect('list_products')
    return render(request, 'add_product.html')

def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.save()
        return redirect('list_products')
    return render(request, 'edit_product.html', {'product': product})

def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('list_products')
    return render(request, 'delete_product.html', {'product': product})

# ====== TÀI KHOẢN ======
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

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# ====== MINI CLOUD (LƯU TRỮ 2TB GOOGLE DRIVE) ======
@login_required
@whitelist_required
def cloud_index(request):
    """Liệt kê file từ Google Drive"""
    try:
        # listdir trả về (directories, files)
        _, files = default_storage.listdir('')
        file_data = []
        for f in files:
            file_data.append({
                'name': f,
                'url': default_storage.url(f),
                'size': default_storage.size(f) if hasattr(default_storage, 'size') else 0
            })
        return render(request, 'cloud_home.html', {'files': file_data})
    except Exception as e:
        return HttpResponse(f"Lỗi truy cập Drive: {e}")

@login_required
@whitelist_required
def upload_file(request):
    """Xử lý upload file thẳng lên Drive"""
    if request.method == 'POST' and request.FILES.get('myfile'):
        myfile = request.FILES['myfile']
        filename = default_storage.save(myfile.name, myfile)
        messages.success(request, f'Đã lưu thành công: {filename}')
    return redirect('cloud_index')

# ====== GAME DATA API (LƯU JSON LÊN DRIVE ĐỂ KHÔNG MẤT DỮ LIỆU) ======
@login_required
def game_data_api(request):
    username = request.user.username
    file_path = f"game_data/{username}.json"

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = json.dumps(data, ensure_ascii=False, indent=4)
            # Xóa file cũ nếu tồn tại để cập nhật
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            default_storage.save(file_path, ContentFile(content))
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    if request.method == 'GET':
        if default_storage.exists(file_path):
            with default_storage.open(file_path, 'r') as f:
                return JsonResponse(json.load(f))
        return JsonResponse({'balance': 1000, 'history': []})
