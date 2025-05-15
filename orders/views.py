from pyexpat.errors import messages
from django.shortcuts import render, redirect
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


# Configurar Stripe con la clave secreta
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def create_checkout_session(request, order_number):
    # Obtener la orden que queremos pagar
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
        cart_items = CartItem.objects.filter(user=request.user)
        
        # Obtener el dominio para las URLs de redirección
        YOUR_DOMAIN = f"{request.scheme}://{request.get_host()}"
        
        # Crear los items para la sesión de Stripe
        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'vnd',
                    'unit_amount': int(item.product.price * 100),  # Stripe necesita el precio en centavos
                    'product_data': {
                        'name': item.product.product_name,
                        'description': item.product.description[:100] if hasattr(item.product, 'description') else '',
                        'images': [f"{YOUR_DOMAIN}{item.product.images.url}"] if hasattr(item.product, 'images') else [],
                    },
                },
                'quantity': item.quantity,
            })
        
        # Crear la sesión de checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'{YOUR_DOMAIN}/orders/success?order_number={order.order_number}&session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{YOUR_DOMAIN}/orders/cancel?order_number={order.order_number}',
            metadata={
                'order_number': order.order_number,
                'user_id': request.user.id,
            }
        )
        
        return JsonResponse({'id': checkout_session.id, 'url': checkout_session.url})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


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

def payment_success(request):
    order_number = request.GET.get('order_number')
    session_id = request.GET.get('session_id')
    
    if not session_id:
        return redirect('home')
    
    try:
        # Verificar la sesión de Stripe para confirmar el pago
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Actualizar la orden con la información de pago
            order = Order.objects.get(order_number=order_number, is_ordered=False)
            
            # Crear un registro de pago
            payment = Payment(
                user=request.user,
                payment_id=session_id,
                payment_method="Stripe",
                amount_paid=order.order_total,
                status="COMPLETED"
            )
            payment.save()
            
            order.payment = payment
            order.is_ordered = True
            order.save()
            
            # Mover los productos del carrito a OrderProduct
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
                
                # Procesar variaciones si existen
                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variations.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()
                
                # Reducir stock
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()
            
            # Limpiar el carrito
            CartItem.objects.filter(user=request.user).delete()
            
            # Enviar correo
            mail_subject = 'Gracias por tu pedido!'
            message = render_to_string('orders/order_recieved_email.html', {
                'user': request.user,
                'order': order,
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            
            # Redirigir a la página de pedido completado
            return redirect('order_complete', order_number=order_number)
    
    except Exception as e:
        return redirect('home')

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
