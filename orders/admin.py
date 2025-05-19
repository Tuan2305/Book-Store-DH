from django.contrib import admin
from .models import Order, OrderProduct, Payment
from django.utils.html import format_html
from django.urls import reverse

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'order_total', 'status', 'payment_status', 'is_ordered', 'created_at', 'actions_btn']
    list_filter = ['status', 'is_ordered', 'created_at']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]
    readonly_fields = ['order_number', 'full_name', 'phone', 'email', 'address', 'city', 'district', 'ward', 'order_total', 'user', 'payment']
    
    def payment_status(self, obj):
        if obj.payment:
            if obj.payment.status == 'COMPLETED':
                return format_html('<span style="color: green; font-weight: bold;">Đã thanh toán</span>')
            elif obj.payment.status == 'PENDING':
                return format_html('<span style="color: orange; font-weight: bold;">Chờ thanh toán</span>')
            else:
                return obj.payment.status
        return '-'
    
    payment_status.short_description = 'Trạng thái thanh toán'
    
    def actions_btn(self, obj):
        update_url = reverse('admin_update_order_status', args=[obj.id])
        view_url = reverse('admin_order_detail', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="margin-right:5px">Cập nhật trạng thái</a>'
            '<a class="button" href="{}" style="background:#417690">Xem chi tiết</a>',
            update_url, view_url
        )
    
    actions_btn.short_description = 'Thao tác'

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)