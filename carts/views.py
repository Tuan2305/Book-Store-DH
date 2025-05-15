from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

@login_required(login_url='login')
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    product_variation = []
    # If the user is authenticated
    if current_user.is_authenticated:
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
                            
                            
    # If the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing_variations -> database
            # current variation -> product_variation
            # item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            print(ex_var_list)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')                
                # try:
                #     cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using the card_id present in the session
                # except Cart.DoesNotExist:
                #     cart = Cart.objects.create(
                #         cart_id = _cart_id(request)
                #     )
                # cart.save()
            
                # try: 
                #     cart_item = CartItem.objects.get(product=product, cart=cart)
                #     cart_item.quantity += 1 
                #     cart_item.save()
                # except CartItem.DoesNotExist:
                #     cart_item = CartItem.objects.create(
                #         product = product,
                #         quantity = 1,
                #         cart = cart,
                #     )
                #     cart_item.save()

                # return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request):
    try:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        if cart_items.count() <= 0:
            return redirect('store')
            
        # Tính toán tổng tiền
        total = 0
        for cart_item in cart_items:
            cart_item.sub_total = cart_item.product.price * cart_item.quantity
            total += cart_item.sub_total
            
        # Lấy thông tin địa chỉ mặc định (nếu có) để prepopulate
        # Nếu bạn có model Address, bạn có thể lấy địa chỉ mặc định
        # default_address = Address.objects.filter(user=request.user, is_default=True).first()
            
        context = {
            'cart_items': cart_items,
            'total': total,
            'user': request.user,
            # 'default_address': default_address,
        }
        return render(request, 'store/checkout.html', context)
    except Exception as e:
        return redirect('cart')

def cart_update_ajax(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')  # Có thể là 'increase', 'decrease', 'remove'
        cart_item_id = request.POST.get('cart_item_id')
        
        if action and product_id:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Sản phẩm không tồn tại'})
            
            # Xử lý người dùng đã đăng nhập
            if request.user.is_authenticated:
                try:
                    if cart_item_id:
                        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
                    else:
                        # Tìm cart_item dựa trên product và user
                        cart_item = CartItem.objects.get(product=product, user=request.user)
                    
                    if action == 'increase':
                        cart_item.quantity += 1
                    elif action == 'decrease':
                        if cart_item.quantity > 1:
                            cart_item.quantity -= 1
                        else:
                            cart_item.delete()
                            return JsonResponse({
                                'removed': True,
                                'product_id': product_id,
                                'cart_item_id': cart_item_id
                            })
                    elif action == 'remove':
                        cart_item.delete()
                        return JsonResponse({
                            'removed': True,
                            'product_id': product_id,
                            'cart_item_id': cart_item_id
                        })
                    
                    cart_item.save()
                    
                    # Tính toán subtotal và total
                    sub_total = cart_item.quantity * cart_item.product.price
                    cart_items = CartItem.objects.filter(user=request.user)
                    total = sum(item.quantity * item.product.price for item in cart_items)
                    
                    return JsonResponse({
                        'status': 'success',
                        'quantity': cart_item.quantity,
                        'sub_total': sub_total,
                        'total': total,
                        'cart_count': sum(item.quantity for item in cart_items)
                    })
                    
                except CartItem.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Sản phẩm không tồn tại trong giỏ hàng'})
            
            # Xử lý người dùng chưa đăng nhập (dùng session)
            else:
                try:
                    # Lấy cart sử dụng cart_id từ session
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    
                    # Tìm cart_item dựa trên product, cart và cart_item_id nếu có
                    if cart_item_id:
                        cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
                    else:
                        # Tìm cart_item dựa trên product và cart
                        cart_item = CartItem.objects.get(product=product, cart=cart)
                    
                    # Xử lý các action tương tự như với user đã đăng nhập
                    if action == 'increase':
                        cart_item.quantity += 1
                    elif action == 'decrease':
                        if cart_item.quantity > 1:
                            cart_item.quantity -= 1
                        else:
                            cart_item.delete()
                            return JsonResponse({
                                'removed': True,
                                'product_id': product_id,
                                'cart_item_id': cart_item_id
                            })
                    elif action == 'remove':
                        cart_item.delete()
                        return JsonResponse({
                            'removed': True,
                            'product_id': product_id,
                            'cart_item_id': cart_item_id
                        })
                    
                    cart_item.save()
                    
                    # Tính toán subtotal và total cho session cart
                    sub_total = cart_item.quantity * cart_item.product.price
                    cart_items = CartItem.objects.filter(cart=cart)
                    total = sum(item.quantity * item.product.price for item in cart_items)
                    
                    return JsonResponse({
                        'status': 'success',
                        'quantity': cart_item.quantity,
                        'sub_total': sub_total,
                        'total': total,
                        'cart_count': sum(item.quantity for item in cart_items)
                    })
                    
                except Cart.DoesNotExist:
                    # Nếu không tìm thấy cart, tạo cart mới
                    return JsonResponse({'status': 'error', 'message': 'Giỏ hàng không tồn tại'})
                except CartItem.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Sản phẩm không tồn tại trong giỏ hàng'})
                except Exception as e:
                    # Bắt các lỗi khác và trả về thông báo lỗi
                    return JsonResponse({'status': 'error', 'message': str(e)})
                
        return JsonResponse({'status': 'error', 'message': 'Dữ liệu không hợp lệ'})
    
    return JsonResponse({'status': 'error', 'message': 'Phương thức không được hỗ trợ'})