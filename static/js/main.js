$('#mob-menu').click(function () {
        $('#mob-topnav').toggleClass('show-mob');
        $('section').slideToggle();
        $('footer').slideToggle();
});

$('#login-focus').on('click',function () {
        $('.login-form').toggleClass('show');
});


HOVERED_ON_LOGO = 0;

$('.logo').hover(function () {
        HOVERED_ON_LOGO+=1;
        console.log(HOVERED_ON_LOGO);
        if(HOVERED_ON_LOGO===10){
                alert('კაი ხოო გადაიწვა ნათურა!!!');
                HOVERED_ON_LOGO=0;
        }
});