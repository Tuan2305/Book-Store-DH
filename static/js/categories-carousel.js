$(document).ready(function() {
    // Điều hướng carousel danh mục
    const scrollAmount = 500;
    const categoriesCarousel = $('.categories-carousel');
    
    $('#categoryPrevBtn').click(function() {
        categoriesCarousel.animate({
            scrollLeft: '-=' + scrollAmount
        }, 300);
    });
    
    $('#categoryNextBtn').click(function() {
        categoriesCarousel.animate({
            scrollLeft: '+=' + scrollAmount
        }, 300);
    });
    
    // Thêm tính năng vuốt cho carousel danh mục trên thiết bị di động
    if ($.fn.swipe) {
        categoriesCarousel.swipe({
            swipeLeft: function() {
                categoriesCarousel.animate({
                    scrollLeft: '+=' + scrollAmount
                }, 300);
            },
            swipeRight: function() {
                categoriesCarousel.animate({
                    scrollLeft: '-=' + scrollAmount
                }, 300);
            },
            threshold: 30,
            allowPageScroll: "vertical"
        });
    }
    
    // Code carousel sách đã có
    $("#bookDealsCarousel .carousel-inner").swipe({
        swipeLeft: function() {
            $("#bookDealsCarousel").carousel('next');
        },
        swipeRight: function() {
            $("#bookDealsCarousel").carousel('prev');
        },
        threshold: 75,
        allowPageScroll: "vertical"
    });
});