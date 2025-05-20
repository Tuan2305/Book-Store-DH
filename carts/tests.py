from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from store.models import Product, Category
from carts.models import Cart, CartItem
from accounts.models import Account

class CartModelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            category_name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            product_name='Test Product',
            slug='test-product',
            price=100.00,
            stock=10,
            is_available=True,
            category=self.category
        )
        # Create a cart for anonymous user
        self.cart = Cart.objects.create(cart_id='test_cart_id')
        self.cart_item = CartItem.objects.create(
            product=self.product,
            cart=self.cart,
            quantity=2
        )
        
    def test_cart_creation(self):
        self.assertEqual(self.cart.cart_id, 'test_cart_id')
        
    def test_cart_item_creation(self):
        self.assertEqual(self.cart_item.product, self.product)
        self.assertEqual(self.cart_item.quantity, 2)
        self.assertEqual(self.cart_item.cart, self.cart)
        
    def test_cart_item_subtotal(self):
        self.assertEqual(self.cart_item.sub_total, 200.00)  # 100 * 2

class CartViewTests(TestCase):
    def setUp(self):
        # Similar setup as CartModelTests
        pass
        
    def test_add_to_cart_view_anonymous_user(self):
        # Test adding item to cart for anonymous user
        pass
        
    def test_add_to_cart_view_logged_in_user(self):
        # Test adding item to cart for logged in user
        pass
        
    # Test remove from cart, update cart, etc.