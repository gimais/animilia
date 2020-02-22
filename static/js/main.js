$('#mob-menu').click(function () {
        $('nav').toggleClass('open');
        $('.top-nav').toggleClass('open')
});

$('#login-focus').on('click',function () {
        $('.login-form').toggleClass('show');
});


HOVERED_ON_LOGO = 0;

$('.logo').hover(function () {
        $('.web-name').toggleClass('web-name-focus');

        HOVERED_ON_LOGO+=1;

        switch(HOVERED_ON_LOGO){
                case 10:
                        alert('კაი ხოო გადაიწვა ნათურა!!!');
                        break;
                case 20:
                        alert('გადაიწვა თქო ბლიად!!!');
                        break;
                case 30:
                        alert('რატომ შეეცი?!!');
                        break;
                case 40:
                        window.location = 'https://www.youtube.com/watch?v=G8iyI_-Amhw';
                        break;
        }
});