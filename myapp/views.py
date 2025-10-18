from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import ProductForm
from .models import Product
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json, os
from django.conf import settings
# ====== JSON DATA FILE ======
DATA_FILE = os.path.join(os.path.dirname(__file__), 'user_data.json')

# Đảm bảo file tồn tại
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)


# ====== TRANG CHÍNH ======
def home(request):
    return render(request, 'home.html')


# ====== QUẢN LÝ SẢN PHẨM ======
def show_products(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'products.html', context)


def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        Product.objects.create(name=name, price=price)
        return redirect('list_products')
    return render(request, 'add_product.html')


def list_products(request):
    products = Product.objects.all()
    return render(request, 'list_products.html', {'products': products})


def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.save()
        return redirect('list_products')
    return render(request, 'edit_product.html', {'product': product})


def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('list_products')
    return render(request, 'delete_product.html', {'product': product})


def new_product(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    return render(request, 'product_form.html', {'form': form})


# ====== TÀI KHOẢN NGƯỜI DÙNG ======
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên tài khoản đã tồn tại!')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Tạo tài khoản thành công!')
            return redirect('login')
    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Sai tài khoản hoặc mật khẩu!')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


# ====== DASHBOARD + LƯU DATA JSON ======
@login_required(login_url='login')
def dashboard(request):
    # XÓA HẾT logic đọc/ghi file JSON cũ ở đây.
    # Hàm này chỉ cần render ra template rỗng.
    # JavaScript sẽ tự gọi 'game_data_api' để điền dữ liệu vào.
    return render(request, 'dashboard.html')


@csrf_exempt
@login_required
def save_data(request):
    """API nhận dữ liệu từ frontend để cập nhật JSON"""
    if request.method == "POST":
        username = request.user.username
        try:
            body = json.loads(request.body)
        except:
            return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data[username] = body

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False}, status=400)
@login_required
def game_data_api(request):
    """API để xử lý việc LẤY (GET) và LƯU (POST) dữ liệu game."""
    
    # Tạo đường dẫn đến thư mục lưu data
    DATA_DIR = os.path.join(settings.BASE_DIR, 'game_data')
    os.makedirs(DATA_DIR, exist_ok=True) # Đảm bảo thư mục này tồn tại
    
    username = request.user.username
    file_path = os.path.join(DATA_DIR, f"{username}.json")

    # Nếu là yêu cầu POST (JavaScript gửi dữ liệu lên để lưu)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return JsonResponse({'status': 'success', 'message': 'Data saved.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    # Nếu là yêu cầu GET (JavaScript muốn lấy dữ liệu khi tải trang)
    if request.method == 'GET':
        if os.path.exists(file_path):
            # Nếu file tồn tại, đọc và trả về
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return JsonResponse(data)
        else:
            # Nếu là người chơi mới (chưa có file), trả về dữ liệu mặc định
            default_data = {
                'balance': 1000,
                'history': []
            }
            return JsonResponse(default_data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)