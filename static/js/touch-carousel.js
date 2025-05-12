$(document).ready(function() {
    // Kiểm tra xem thư viện TouchSwipe đã được tải chưa
    if ($.fn.swipe) {
        // Kích hoạt tính năng vuốt cho carousel với cấu hình tối ưu
        $("#bookDealsCarousel .carousel-inner").swipe({
            swipeLeft: function() {
                $("#bookDealsCarousel").carousel('next');
            },
            swipeRight: function() {
                $("#bookDealsCarousel").carousel('prev');
            },
            threshold: 30,  // Giảm ngưỡng để dễ vuốt hơn
            preventDefaultEvents: false,
            allowPageScroll: "vertical"
        });
        
        // Thêm chỉ báo rõ ràng cho người dùng biết có thể vuốt
        $("#bookDealsCarousel").append('<div class="swipe-indicator d-md-none">Vuốt để xem thêm</div>');
    }
});

$(document).ready(function() {
    // Tính năng swipe cho thiết bị cảm ứng
    if ($.fn.swipe) {
        $("#bookDealsCarousel .carousel-inner").swipe({
            swipeLeft: function() {
                $("#bookDealsCarousel").carousel('next');
            },
            swipeRight: function() {
                $("#bookDealsCarousel").carousel('prev');
            },
            threshold: 30,
            preventDefaultEvents: false,
            allowPageScroll: "vertical"
        });
    }
    
    // Thêm tính năng kéo thả bằng chuột (mouse drag)
    let isDragging = false;
    let startPosition = 0;
    let currentTranslate = 0;
    
    $("#bookDealsCarousel .carousel-inner").mousedown(function(e) {
        isDragging = true;
        startPosition = e.pageX - $(this).offset().left;
        $(this).css('cursor', 'grabbing');
        e.preventDefault();
    });
    
    $(document).mouseup(function() {
        if (isDragging) {
            isDragging = false;
            $("#bookDealsCarousel .carousel-inner").css('cursor', 'grab');
            
            // Xác định hướng cuộn dựa vào khoảng cách kéo
            if (currentTranslate > 50) {
                $("#bookDealsCarousel").carousel('prev');
            } else if (currentTranslate < -50) {
                $("#bookDealsCarousel").carousel('next');
            }
            
            currentTranslate = 0;
        }
    });
    
    $(document).mousemove(function(e) {
        if (isDragging) {
            const x = e.pageX - $("#bookDealsCarousel .carousel-inner").offset().left;
            currentTranslate = x - startPosition;
        }
    });
    
    // Thêm các nút điều hướng bằng bàn phím
    $(document).keydown(function(e) {
        if (e.keyCode == 37) { // mũi tên trái
            $("#bookDealsCarousel").carousel('prev');
        }
        else if (e.keyCode == 39) { // mũi tên phải
            $("#bookDealsCarousel").carousel('next');
        }
    });
    
    // Thêm tính năng scroll wheel để di chuyển carousel
    $("#bookDealsCarousel").on('wheel', function(e) {
        if(e.originalEvent.deltaY > 0) {
            $(this).carousel('next');
        } else {
            $(this).carousel('prev');
        }
        e.preventDefault();
    });
    
    // Thêm chỉ dẫn cách sử dụng
    $("#bookDealsCarousel").append('<div class="usage-tips d-none d-md-block">Dùng phím mũi tên ← → hoặc click và kéo để di chuyển</div>');
});

$(document).ready(function() {
    // Kích hoạt nút điều khiển tròn
    $(".carousel-nav-btn").click(function(e) {
        e.preventDefault();
        const target = $(this).attr("href");
        const slideDirection = $(this).data("slide");
        $(target).carousel(slideDirection);
    });
    
    // Code xử lý vuốt và các tính năng khác giữ nguyên
});
