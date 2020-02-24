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


function activateClassButton(button){
       var activatedButton = $('.item-page-episodes').find('.episode-select-button.active');
       if(button!==activatedButton) {
               activatedButton.removeClass('active');
               button.addClass('active');
       }
}

function setCookie(name, value, expire,path) {
        var date = new Date();
        date.setTime(date.getTime() + (expire*24*60*60*1000));
        var expires = "expires="+ date.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/" + path;
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

const locationURL = document.location.href;
const itemSlug = locationURL.substring(21,locationURL.length-1);

window.onload = function(){
  if(itemSlug.substring(0,7)==='/anime/'){
          var pageCookie = getCookie(itemSlug.substring(7));
          if(pageCookie!==""){
                  $('.item-page-episodes').find(`.episode-select-button[data-id=${pageCookie}]`).addClass('active');
          }
  }
};

$('.episode-select-button').on('click',function () {
        var clickedButton = $(this);
        activateClassButton(clickedButton);
        var videoURL = clickedButton.data('url');
        $('.item-player iframe').attr('src',videoURL);
        if ($('.item-player').hasClass('hidden')) {
                $('.item-player').removeClass('hidden');
        }
        setCookie(locationURL.substring(28,locationURL.length-1),clickedButton.data('id'),10,locationURL.substring(22));
});
