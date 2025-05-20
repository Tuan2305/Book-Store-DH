from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
import stripe
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Configurar Stripe con la clave secreta
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def create_checkout_session(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
        cart_items = CartItem.objects.filter(user=request.user)
        
        # Lưu thông tin đơn hàng vào session
        request.session['pending_order_number'] = order_number
        request.session['pending_order_id'] = order.id
        
        YOUR_DOMAIN = f"{request.scheme}://{request.get_host()}"
        
        # Tạo các items cho phiên thanh toán Stripe
        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'vnd',
                    'unit_amount': int(item.product.price),
                    'product_data': {
                        'name': item.product.product_name,
                        'description': item.product.description[:100] if hasattr(item.product, 'description') else '',
                        'images': [f"{YOUR_DOMAIN}{item.product.images.url}"] if hasattr(item.product, 'images') else [],
                    },
                },
                'quantity': item.quantity,
            })
        
        # Tạo phiên thanh toán với URL thành công chứa payment_intent
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'{YOUR_DOMAIN}/orders/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{YOUR_DOMAIN}/orders/cancel?order_number={order.order_number}',
            metadata={
                'order_number': order.order_number,
                'user_id': request.user.id,
            }
        )
        
        # Lưu thông tin phiên thanh toán để sử dụng sau này
        request.session['checkout_session_id'] = checkout_session.id
        
        return JsonResponse({'id': checkout_session.id, 'url': checkout_session.url})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def payment_success(request):
    # Lấy session_id từ URL query parameters
    session_id = request.GET.get('session_id')
    
    try:
        if not session_id:
            raise Exception('Không tìm thấy session_id trong URL')
            
        # Lấy thông tin phiên thanh toán từ Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Lấy thông tin đơn hàng từ session
        order_number = request.session.get('pending_order_number')
        
        if not order_number:
            order_number = checkout_session.metadata.get('order_number')
            
        # Lấy đơn hàng từ database
        order = Order.objects.get(order_number=order_number, user=request.user)
        
        # Tạo bản ghi thanh toán mới
        payment = Payment(
            user=request.user,
            payment_id=checkout_session.payment_intent,
            payment_method='Stripe',
            amount_paid=order.order_total,
            status='COMPLETED'
        )
        payment.save()
        
        # Lưu thông tin payment_id vào session để sử dụng ở trang success
        request.session['order_id'] = order.id
        request.session['payment_id'] = payment.id
        
        # Cập nhật trạng thái đơn hàng
        order.payment = payment
        order.is_ordered = True
        order.status = 'Completed'
        order.save()
        
        # Cập nhật sản phẩm đã đặt
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()
            
            # Cập nhật số lượng sản phẩm
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()
        
        # Xóa giỏ hàng
        CartItem.objects.filter(user=request.user).delete()
        
        # Hiển thị trang thành công với thông tin đơn hàng
        ordered_products = OrderProduct.objects.filter(order=order)
        context = {
            'order': order,
            'payment': payment,
            'ordered_products': ordered_products,
        }
        
        # Xóa session data
        if 'pending_order_number' in request.session:
            del request.session['pending_order_number']
        if 'pending_order_id' in request.session:
            del request.session['pending_order_id']
        if 'checkout_session_id' in request.session:
            del request.session['checkout_session_id']
            
        return render(request, 'orders/success.html', context)
        
    except Exception as e:
        print(f"Lỗi trong payment_success: {str(e)}")
        messages.error(request, f'Đã xảy ra lỗi khi xử lý thanh toán: {str(e)}')
        return redirect('cart')


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            
            data.city = form.cleaned_data['city']
            data.district = form.cleaned_data['district']
            data.ward = form.cleaned_data['ward']
            data.address = form.cleaned_data['address']
         
            data.order_note = form.cleaned_data['order_note']
            data.order_total = total
            data.tax = 0 
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')

# def payment_success(request):
#     # Lấy thông tin từ session
#     order_id = request.session.get('order_id')
#     payment_id = request.session.get('payment_id')
    
#     try:
#         order = Order.objects.get(id=order_id, user=request.user)
#         # Cập nhật trạng thái đơn hàng ngay tại đây
#         order.status = 'Completed'
#         order.is_ordered = True
#         order.save()
        
#         payment = Payment.objects.get(payment_id=payment_id)
#         # Cập nhật trạng thái thanh toán
#         payment.status = 'COMPLETED'
#         payment.save()
        
#         # Cập nhật số lượng sản phẩm trong kho
#         ordered_products = OrderProduct.objects.filter(order=order)
#         for item in ordered_products:
#             product = Product.objects.get(id=item.product.id)
#             product.stock -= item.quantity
#             product.save()
        
#         # Xóa giỏ hàng sau khi thanh toán thành công
#         CartItem.objects.filter(user=request.user).delete()
        
#         ordered_products = OrderProduct.objects.filter(order=order)
#         context = {
#             'order': order,
#             'payment': payment,
#             'ordered_products': ordered_products,
#         }
        
#         # Xóa session khi đã hiển thị thành công
#         if 'order_id' in request.session:
#             del request.session['order_id']
#         if 'payment_id' in request.session:
#             del request.session['payment_id']
            
#         return render(request, 'orders/success.html', context)
    
#     except (Order.DoesNotExist, Payment.DoesNotExist):
#         return redirect('home')

def payment_cancel(request):
    order_number = request.GET.get('order_number')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
        # Aquí puedes decidir si eliminar la orden o marcarla como cancelada
        # order.delete()
        
        # O simplemente devolver al usuario al carrito o a un mensaje
        messages.error(request, "El pago ha sido cancelado. Por favor, inténtalo de nuevo.")
        return redirect('cart')
    except:
        return redirect('home')



def order_complete(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        payment = order.payment
        
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
            
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')

# orders/views.py
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Xử lý event payment_intent.succeeded
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Lấy đơn hàng và cập nhật trạng thái
        try:
            order_number = session.metadata.order_number
            order = Order.objects.get(order_number=order_number)
            
            # Cập nhật trạng thái đơn hàng và thanh toán
            payment = Payment.objects.get(order=order)
            payment.status = 'COMPLETED'
            payment.save()
            
            order.status = 'Completed'
            order.is_ordered = True
            order.save()
            
        except Exception as e:
            print(str(e))
            
    return HttpResponse(status=200)

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        status_notes = request.POST.get('status_notes', '')
        
        # Lưu trạng thái trước khi thay đổi
        old_status = order.status
        
        # Cập nhật trạng thái
        order.status = new_status
        order.status_notes = status_notes
        
        # Cập nhật thời gian tương ứng với trạng thái
        if new_status == 'Processing' and old_status != 'Processing':
            order.processed_at = timezone.now()
        elif new_status == 'Shipping' and old_status != 'Shipping':
            order.shipped_at = timezone.now()
        elif new_status == 'Delivered' and old_status != 'Delivered':
            order.delivered_at = timezone.now() 
        elif new_status == 'Completed' and old_status != 'Completed':
            order.completed_at = timezone.now()
        elif new_status == 'Cancelled' and old_status != 'Cancelled':
            order.cancelled_at = timezone.now()
            
        order.save()
        
        # Gửi email thông báo đến khách hàng
        subject = f'Cập nhật trạng thái đơn hàng #{order.order_number}'
        message = f'Đơn hàng của bạn đã được cập nhật sang trạng thái: {dict(Order.STATUS_CHOICES)[new_status]}'
        if status_notes:
            message += f'\n\nGhi chú: {status_notes}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email])
        
        messages.success(request, f'Trạng thái đơn hàng đã được cập nhật thành {dict(Order.STATUS_CHOICES)[new_status]}')
        return redirect('admin_order_detail', order_id=order.id)
        
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'admin/orders/order_status_update.html', context)

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    ordered_products = OrderProduct.objects.filter(order=order)
    
    context = {
        'order': order,
        'ordered_products': ordered_products,
    }
    return render(request, 'admin/orders/order_detail.html', context)

@login_required(login_url='login')
def cancel_order(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        
        # Chỉ cho phép hủy đơn hàng khi đang ở trạng thái New hoặc Processing
        if order.status in ['New', 'Processing']:
            if request.method == 'POST':
                cancel_reason = request.POST.get('cancel_reason', '')
                other_reason = request.POST.get('other_reason', '')
                
                if cancel_reason == 'other' and other_reason:
                    final_reason = other_reason
                else:
                    final_reason = cancel_reason
                
                order.status = 'Cancelled'
                order.cancelled_at = timezone.now()
                order.cancel_reason = final_reason
                order.save()
                
                messages.success(request, 'Đơn hàng đã được hủy thành công.')
                return redirect('order_detail', order_number=order_number)
            
            return render(request, 'orders/cancel_order.html', {'order': order})
        else:
            messages.error(request, 'Bạn không thể hủy đơn hàng này vì nó đang được vận chuyển hoặc đã hoàn thành.')
            return redirect('order_detail', order_number=order_number)
    except Order.DoesNotExist:
        messages.error(request, 'Đơn hàng không tồn tại.')
        return redirect('my_orders')