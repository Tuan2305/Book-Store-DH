from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Account

class AccountModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '0123456789',
            'password': 'TestPass123!',
        }
        self.user = Account.objects.create_user(**self.user_data)
    
    def test_create_user(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('TestPass123!'))
        self.assertFalse(self.user.is_admin)
        
    def test_create_superuser(self):
        admin = Account.objects.create_superuser(
            'admin@example.com', 'adminuser', 'AdminPass123!')
        self.assertTrue(admin.is_admin)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superadmin)
        
    def test_user_email_unique(self):
        """Test email là duy nhất trong hệ thống"""
        with self.assertRaises(Exception):
            Account.objects.create_user(
                first_name='Another',
                last_name='User',
                username='anotheruser',
                email='test@example.com',  # Email trùng với user đã tạo trong setUp
                phone_number='0987654321',
                password='AnotherPass123!'
            )
        
    def test_username_unique(self):
        """Test username là duy nhất trong hệ thống"""
        with self.assertRaises(Exception):
            Account.objects.create_user(
                first_name='Another',
                last_name='User',
                username='testuser',  # Username trùng với user đã tạo trong setUp
                email='another@example.com',
                phone_number='0987654321',
                password='AnotherPass123!'
            )
            
    def test_required_fields(self):
        """Test các trường bắt buộc"""
        with self.assertRaises(ValueError):
            Account.objects.create_user(
                first_name='',
                last_name='User',
                username='',  # Username trống
                email='',  # Email trống
                password='TestPass123!'
            )
            
    def test_default_values(self):
        """Test giá trị mặc định khi tạo user"""
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_active)  # Mặc định là không active vì cần xác thực email
        self.assertFalse(self.user.is_superadmin)
        
    # More model tests...

class AccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')
        self.user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '0123456789',
            'password': 'TestPass123!',
        }
        
    def test_registration_view_GET(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        
    def test_registration_view_POST_valid(self):
        response = self.client.post(self.register_url, {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '0123456789',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
        })
        self.assertEqual(Account.objects.count(), 1)
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
    # More view tests...
    def test_login_view_GET(self):
        """Test hiển thị trang đăng nhập"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_view_POST_valid(self):
        """Test đăng nhập thành công"""
        # Tạo user trước
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect sau khi đăng nhập thành công

    def test_login_view_POST_invalid_password(self):
        """Test đăng nhập với mật khẩu không đúng"""
        # Tạo user trước
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        })
        self.assertEqual(response.status_code, 200)  # Trở lại form đăng nhập
        self.assertContains(response, 'Mật khẩu không chính xác')

    def test_login_view_POST_inactive_user(self):
        """Test đăng nhập với tài khoản chưa kích hoạt"""
        # Tạo user chưa kích hoạt
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        # mặc định is_active = False
        
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tài khoản chưa được kích hoạt')

    def test_dashboard_view_authenticated(self):
        """Test truy cập trang dashboard khi đã đăng nhập"""
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        self.client.login(email='test@example.com', password='TestPass123!')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard.html')

    def test_dashboard_view_unauthenticated(self):
        """Test truy cập trang dashboard khi chưa đăng nhập"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logout_view(self):
        """Test logout thành công"""
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        self.client.login(email='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect sau khi logout

    def test_edit_profile_view_GET(self):
        """Test hiển thị trang chỉnh sửa thông tin"""
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        self.client.login(email='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/edit_profile.html')

    def test_edit_profile_view_POST(self):
        """Test cập nhật thông tin cá nhân"""
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        self.client.login(email='test@example.com', password='TestPass123!')
        response = self.client.post(reverse('edit_profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '0987654321',
            'email': 'test@example.com'  # Email không thay đổi
        })
        self.assertEqual(response.status_code, 302)  # Redirect sau khi cập nhật
        
        # Kiểm tra thông tin đã được cập nhật
        updated_user = Account.objects.get(email='test@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.phone_number, '0987654321')

    def test_change_password_view_GET(self):
        """Test hiển thị trang đổi mật khẩu"""
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        self.client.login(email='test@example.com', password='TestPass123!')
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/change_password.html')

    def test_change_password_view_POST_valid(self):
        """Test đổi mật khẩu thành công"""
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        self.client.login(email='test@example.com', password='TestPass123!')
        response = self.client.post(reverse('change_password'), {
            'current_password': 'TestPass123!',
            'new_password': 'NewPass456@',
            'confirm_password': 'NewPass456@'
        })
        self.assertEqual(response.status_code, 302)  # Redirect sau khi đổi mật khẩu
        
        # Kiểm tra mật khẩu đã được thay đổi
        updated_user = Account.objects.get(email='test@example.com')
        self.assertTrue(updated_user.check_password('NewPass456@'))

    def test_change_password_view_POST_wrong_current(self):
        """Test đổi mật khẩu với mật khẩu hiện tại không đúng"""
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        self.client.login(email='test@example.com', password='TestPass123!')
        response = self.client.post(reverse('change_password'), {
            'current_password': 'WrongPass123!',
            'new_password': 'NewPass456@',
            'confirm_password': 'NewPass456@'
        })
        self.assertEqual(response.status_code, 302)  # Redirect back to change password page
        
        # Kiểm tra mật khẩu không thay đổi
        updated_user = Account.objects.get(email='test@example.com')
        self.assertTrue(updated_user.check_password('TestPass123!'))

    def test_change_password_view_POST_mismatch(self):
        """Test đổi mật khẩu với mật khẩu mới và xác nhận không khớp"""
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        self.client.login(email='test@example.com', password='TestPass123!')
        response = self.client.post(reverse('change_password'), {
            'current_password': 'TestPass123!',
            'new_password': 'NewPass456@',
            'confirm_password': 'DifferentPass789#'
        })
        self.assertEqual(response.status_code, 302)  # Redirect back to change password page
        
        # Kiểm tra mật khẩu không thay đổi
        updated_user = Account.objects.get(email='test@example.com')
        self.assertTrue(updated_user.check_password('TestPass123!'))

    def test_forgot_password_view_GET(self):
        """Test hiển thị trang quên mật khẩu"""
        response = self.client.get(reverse('forgotPassword'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/forgotPassword.html')

    def test_forgot_password_view_POST_valid(self):
        """Test yêu cầu reset mật khẩu với email tồn tại"""
        user = Account.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser',
            email='test@example.com',
            phone_number='0123456789',
            password='TestPass123!'
        )
        user.is_active = True
        user.save()
        
        response = self.client.post(reverse('forgotPassword'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 200)
        # Check for success message
        self.assertContains(response, 'Hướng dẫn đặt lại mật khẩu')

class AccountFormTests(TestCase):
    """Tests cho các form trong app accounts"""
    
    def test_registration_form_valid(self):
        """Test form đăng ký với dữ liệu hợp lệ"""
        from accounts.forms import RegistrationForm
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '0123456789',
            'email': 'testuser@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_registration_form_password_mismatch(self):
        """Test form đăng ký với mật khẩu và xác nhận không khớp"""
        from accounts.forms import RegistrationForm
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '0123456789',
            'email': 'testuser@example.com',
            'password': 'TestPass123',
            'confirm_password': 'DifferentPass456',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)
    
    def test_registration_form_email_exists(self):
        """Test form đăng ký với email đã tồn tại"""
        # Tạo user với email cụ thể
        Account.objects.create_user(
            first_name='Existing',
            last_name='User',
            username='existinguser',
            email='existing@example.com',
            phone_number='0987654321',
            password='ExistingPass123!'
        )
        
        from accounts.forms import RegistrationForm
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '0123456789',
            'email': 'existing@example.com',  # Email đã tồn tại
            'password': 'TestPass123',
            'confirm_password': 'TestPass123',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_registration_form_weak_password(self):
        """Test form đăng ký với mật khẩu yếu (nếu có validation)"""
        from accounts.forms import RegistrationForm
        form_data = {
            'first_name': 'Test',
            'last_name': 'User', 
            'phone_number': '0123456789',
            'email': 'testuser@example.com',
            'password': '123',  # Mật khẩu quá ngắn/đơn giản
            'confirm_password': '123',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)