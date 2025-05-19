from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)
    
    list_filter = ('is_active', 'is_staff', 'is_admin')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    fieldsets = (
        ('Thông tin tài khoản', {'fields': ('email', 'username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Quyền hạn', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superadmin')}),
        ('Quan trọng', {'fields': ('last_login', 'date_joined')}),
    )

    filter_horizontal = ()
    list_per_page = 20

# Đăng ký với cả admin site mặc định và custom admin site
admin.site.register(Account, AccountAdmin)

