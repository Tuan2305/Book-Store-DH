from django.urls import path
from . import views

urlpatterns = [
    # URLs hiện tại
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('success/', views.payment_success, name='payment_success'),
    path('create-checkout-session/<str:order_number>/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    
    # URLs mới cho quản lý trạng thái đơn hàng
    path('cancel-order/<str:order_number>/', views.cancel_order, name='cancel_order'),
    path('admin/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/order/<int:order_id>/update-status/', views.update_order_status, name='admin_update_order_status'),
]