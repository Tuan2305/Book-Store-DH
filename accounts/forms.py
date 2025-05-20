from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Nhập mật khẩu',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Xác nhận mật khẩu'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def clean_password(self):
        """Kiểm tra yêu cầu mật khẩu mạnh"""
        password = self.cleaned_data.get('password')
        
        # Kiểm tra độ dài tối thiểu
        if len(password) < 8:
            raise forms.ValidationError('Mật khẩu phải có ít nhất 8 ký tự.')
        
        # Kiểm tra có chữ cái
        if not any(char.isalpha() for char in password):
            raise forms.ValidationError('Mật khẩu phải chứa ít nhất một chữ cái.')
        
        # Kiểm tra có chữ số
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError('Mật khẩu phải chứa ít nhất một chữ số.')
        
        # Kiểm tra có ký tự đặc biệt
        if not any(not char.isalnum() for char in password):
            raise forms.ValidationError('Mật khẩu phải chứa ít nhất một ký tự đặc biệt.')
        
        return password

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                "Mật khẩu không khớp!"
            )
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Nhập họ'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Nhập tên'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Nhập số điện thoại'
        self.fields['email'].widget.attrs['placeholder'] = 'Nhập địa chỉ email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'