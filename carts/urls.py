from django.urls import path
from . import views

urlpatterns = [
    # Các urls hiện có
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    
    # URL mới cho API AJAX
    path('update_cart_ajax/', views.cart_update_ajax, name='update_cart_ajax'),
    path('add_cart_ajax/<int:product_id>/', views.add_cart_ajax, name='add_cart_ajax'),
    # Thêm URL cho checkout
    path('checkout/', views.checkout, name='checkout'),
]