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

# ====== DECORATOR WHITE LIST ======
def whitelist_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.username in getattr(settings, 'CLOUD_WHITELIST', []):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

# ====== TRANG CHÍNH & SẢN PHẨM (GIỮ NGUYÊN) ======
def home(request):
    return render(request, 'home.html')

def list_products(request):
    # Lưu ý: Product lưu trong db.sqlite3 vẫn sẽ bị mất nếu Render restart
    # Trừ khi ông dùng Database rời (Postgres)
    from .models import Product
    products = Product.objects.all()
    return render(request, 'list_products.html', {'products': products})

# ====== TÀI KHOẢN (GIỮ NGUYÊN) ======
def user_login(request):
    if request.method == 'POST':
        u, p = request.POST.get('username'), request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Sai tài khoản hoặc mật khẩu!')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

# ====== MINI CLOUD (MỚI) ======
@login_required
@whitelist_required
def cloud_index(request):
    """Liệt kê file từ Google Drive 2TB"""
    try:
        # Lấy danh sách file từ thư mục gốc của Drive đã config
        _, files = default_storage.listdir('')
        file_data = []
        for f in files:
            file_data.append({
                'name': f,
                'url': default_storage.url(f),
                'size': default_storage.size(f) if hasattr(default_storage, 'size') else "N/A"
            })
        return render(request, 'cloud_home.html', {'files': file_data})
    except Exception as e:
        return HttpResponse(f"Lỗi Drive: {e}")

# ====== GAME DATA API (ĐÃ FIX ĐỂ KHÔNG MẤT DỮ LIỆU) ======
@login_required
def game_data_api(request):
    username = request.user.username
    file_path = f"game_data/{username}.json"

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = json.dumps(data, ensure_ascii=False, indent=4)
            # Lưu thẳng lên Google Drive
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
@login_required
@whitelist_required
def upload_file(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        filename = default_storage.save(myfile.name, myfile)
        messages.success(request, f'Đã upload: {filename}')
    return redirect('cloud_index')
