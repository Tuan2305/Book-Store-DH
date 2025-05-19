from django.db import models
from accounts.models import Account
from store.models import Product



class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100) # this is the total amount paid
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS_CHOICES = (
        ('New', 'Mới'),
        ('Processing', 'Đang chuẩn bị'),
        ('Shipping', 'Đang vận chuyển'),
        ('Delivered', 'Đã giao hàng'),
        ('Completed', 'Hoàn thành'),
        ('Cancelled', 'Đã hủy'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    
    # Add these new fields
    city = models.CharField(max_length=50, blank=True)
    district = models.CharField(max_length=50, blank=True)
    ward = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=100, blank=True)
    
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='New')
    
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

     # Thêm trường lý do hủy đơn
    cancel_reason = models.TextField(blank=True, null=True)
    # Thêm trường ghi chú cập nhật trạng thái
    status_notes = models.TextField(blank=True, null=True)
    # Thêm các trường thời gian cho từng trạng thái
    processed_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'orders'

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orderproducts'

    def __str__(self):
        return self.product.product_name
    
    def sub_total(self):
        return self.product_price * self.quantity

