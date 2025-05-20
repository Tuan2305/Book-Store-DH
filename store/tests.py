from django.test import TestCase
from django.urls import reverse
from store.models import Product, Category, ReviewRating
from accounts.models import Account

class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            category_name='Test Category',
            slug='test-category',
            description='Test category description'
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.category_name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        
    def test_category_str_representation(self):
        self.assertEqual(str(self.category), 'Test Category')
        
    def test_get_url_method(self):
        self.assertEqual(self.category.get_url(), '/store/category/test-category/')

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            category_name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            product_name='Test Product',
            slug='test-product',
            description='Test description',
            price=100.00,
            stock=10,
            is_available=True,
            category=self.category
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.product_name, 'Test Product')
        self.assertEqual(self.product.price, 100.00)
        self.assertEqual(self.product.category, self.category)
        
    # More product model tests...

class StoreViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            category_name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            product_name='Test Product',
            slug='test-product',
            description='Test description',
            price=100.00,
            stock=10,
            is_available=True,
            category=self.category
        )
        self.store_url = reverse('store')
        self.product_detail_url = reverse('product_detail', 
                                         args=['test-category', 'test-product'])
        
    def test_store_view_GET(self):
        response = self.client.get(self.store_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/store.html')
        self.assertIn(self.product, response.context['products'])
        
    def test_product_detail_view_GET(self):
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product_detail.html')
        self.assertEqual(response.context['single_product'], self.product)

    # More store view tests...

class ReviewTests(TestCase):
    # Test review creation, updating, etc.
    pass