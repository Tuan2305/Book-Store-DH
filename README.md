📚 Book Store – Hệ thống bán sách trực tuyến
Book Store là một dự án web thương mại điện tử chuyên về bán sách, phát triển bằng Django. Hệ thống cho phép người dùng duyệt sách, đặt hàng và thanh toán trực tuyến.

🔧 Công nghệ sử dụng
    Backend: Django 5.1.2
    Frontend: HTML, CSS, JavaScript, Bootstrap
    Database: MySQL
    Thanh toán: Stripe API
    Xác thực: Django Authentication System

📁 Cấu trúc dự án
Book-Store-New/
    ├── accounts/       # Quản lý người dùng: đăng nhập, đăng ký, thông tin cá nhân
    ├── carts/          # Giỏ hàng: thêm, xóa, cập nhật sản phẩm
    ├── category/       # Quản lý danh mục sách
    ├── greatkart/      # Cấu hình chính của dự án Django
    ├── media/          # Lưu trữ hình ảnh sản phẩm
    ├── orders/         # Xử lý đơn hàng và thanh toán
    ├── static/         # CSS, JavaScript, hình ảnh tĩnh
    ├── store/          # Quản lý sản phẩm và giao diện cửa hàng
    └── templates/      # Các template HTML

✨ Các chức năng chính
1. 👤 Quản lý người dùng
    Đăng ký, đăng nhập, đăng xuất
    Cập nhật thông tin cá nhân
    Quản lý địa chỉ giao hàng
    Đổi mật khẩu, quên mật khẩu (gửi email khôi phục)

2. 📦 Quản lý sản phẩm
    Xem danh sách sản phẩm theo danh mục
    Tìm kiếm và xem chi tiết sản phẩm
    Đánh giá và xếp hạng sản phẩm

3. 🛒 Giỏ hàng
    Thêm sản phẩm vào giỏ hàng
    Cập nhật số lượng, xóa sản phẩm
    Tính tổng tiền

4. 💳 Đặt hàng & Thanh toán
    Điền thông tin giao hàng
    Thanh toán qua Stripe (Thẻ tín dụng/Ghi nợ)
    Xử lý thanh toán an toàn
    Theo dõi trạng thái đơn hàng

5. 🔍 Tính năng bổ sung
    Danh sách yêu thích
    Lịch sử đơn hàng
    Bảng điều khiển người dùng
    Carousel sản phẩm nổi bật
    Responsive: Giao diện thân thiện với thiết bị di động

🛒 Quy trình mua hàng
    Người dùng đăng ký/đăng nhập vào hệ thống
    Duyệt sản phẩm và thêm vào giỏ hàng
    Xem giỏ hàng và tiến hành thanh toán
    Điền thông tin giao hàng
    Chọn phương thức thanh toán (Stripe)
    Hoàn tất thanh toán
    Nhận xác nhận đơn hàng
    Theo dõi trạng thái đơn hàng

🚀 Cài đặt và chạy dự án
1. Clone dự án

git clone <repository-url>
cd Book-Store-New

2. Tạo môi trường ảo và cài đặt phụ thuộc

python -m venv venv
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

3. Thiết lập cơ sở dữ liệu
python manage.py migrate
4. Tạo tài khoản admin
python manage.py createsuperuser
5. Chạy server
python manage.py runserver
6. Truy cập hệ thống
    Trang chủ: http://127.0.0.1:8000/

    Admin: http://127.0.0.1:8000/admin/

💳 Cấu hình Stripe (Thanh toán)
    Đăng ký tài khoản tại: https://stripe.com
    Lấy API keys từ Stripe Dashboard
    Cập nhật các keys vào file settings.py: 

    STRIPE_PUBLISHABLE_KEY = 'your-publishable-key'
    STRIPE_SECRET_KEY = 'your-secret-key