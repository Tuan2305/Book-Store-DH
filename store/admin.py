from django.contrib import admin
from .models import Product,Variation, ReviewRating


# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')

admin.site.register(Product, ProductAdmin)
# admin.site.register(Variation, VariationAdmin)
# admin.site.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'subject', 'rating', 'created_at', 'status')
    list_filter = ('status', 'rating')
    search_fields = ('subject', 'review', 'user__email', 'product__product_name')
    list_editable = ('status',)
    
admin.site.register(ReviewRating, ReviewRatingAdmin)