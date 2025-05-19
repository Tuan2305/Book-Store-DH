from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating
from category.models import Category
from carts.models import CartItem
from django.db.models import Q
from django.db.models import Avg
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required

def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        
    # Lấy các tham số lọc giá từ request
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 500000)
    
    # Chuyển đổi giá trị thành số (với xử lý lỗi)
    try:
        min_price = int(min_price)
    except (ValueError, TypeError):
        min_price = 0
        
    try:
        max_price = int(max_price)
    except (ValueError, TypeError):
        max_price = 500000
    
    # Lọc sản phẩm theo khoảng giá
    products = products.filter(price__gte=min_price, price__lte=max_price)
    
    # Lọc theo từ khóa nếu có
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            # Tìm kiếm trong tên hoặc mô tả sản phẩm
            products = products.filter(Q(product_name__icontains=keyword) | 
                                     Q(description__icontains=keyword))
    
    product_count = products.count()
    
    # Phân trang
    paginator = Paginator(products, 6)  # 6 sản phẩm mỗi trang
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    
    context = {
        'products': paged_products,
        'product_count': product_count,
        'category_slug': category_slug,
        'min_price': min_price,
        'max_price': max_price,
    }
    
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    # reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'orderproduct': orderproduct,
        # 'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    products = None
    product_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
        'links': Category.objects.all(),
    }
    return render(request, 'store/store.html', context)


# def submit_review(request, product_id):
#     url = request.META.get('HTTP_REFERER')
#     if request.method == 'POST':
#         try:
#             reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
#             form = ReviewForm(request.POST, instance=reviews)
#             form.save()
#             messages.success(request, 'Thank you! Your review has been updated.')
#             return redirect(url)
#         except ReviewRating.DoesNotExist:
#             form = ReviewForm(request.POST)
#             if form.is_valid():
#                 data = ReviewRating()
#                 data.subject = form.cleaned_data['subject']
#                 data.rating = form.cleaned_data['rating']
#                 data.review = form.cleaned_data['review']
#                 data.ip = request.META.get('REMOTE_ADDR')
#                 data.product_id = product_id
#                 data.user_id = request.user.id
#                 data.save()
#                 messages.success(request, 'Thank you! Your review has been submitted.')
#                 return redirect(url)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    # Kiểm tra xem người dùng đã mua sản phẩm chưa (có thể skip nếu bạn muốn ai cũng được đánh giá)
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Lấy các đánh giá
    reviews = ReviewRating.objects.filter(product=single_product, status=True).order_by('-created_at')
    
    # Tính rating trung bình
    if reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        review_count = reviews.count()
        
        # Phân phối rating
        rating_counts = {
            5: reviews.filter(rating=5).count(),
            4: reviews.filter(rating=4).count(),
            3: reviews.filter(rating=3).count(),
            2: reviews.filter(rating=2).count(),
            1: reviews.filter(rating=1).count(),
        }
        
        # Tính phần trăm
        for rating, count in rating_counts.items():
            rating_counts[rating] = (count / review_count) * 100 if review_count > 0 else 0
    else:
        avg_rating = 0
        review_count = 0
        rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'rating_counts': rating_counts,
    }
    return render(request, 'store/product_detail.html', context)

@login_required(login_url='login')
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            # Kiểm tra xem người dùng đã đánh giá sản phẩm này chưa
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            # Nếu đã tồn tại, cập nhật đánh giá
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Cảm ơn bạn! Đánh giá của bạn đã được cập nhật.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            # Tạo đánh giá mới
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Cảm ơn bạn! Đánh giá của bạn đã được gửi.')
                return redirect(url)
    
    # Cho GET request hoặc lỗi form
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'store/submit_review.html', context)


def home(request):
    products = Product.objects.all().filter(is_available=True)
    categories = Category.objects.all()
    
    print("Categories count:", categories.count())  # Kiểm tra số lượng categories
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'home.html', context)