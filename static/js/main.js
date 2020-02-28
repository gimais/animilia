// ANIMILIA JAVASCRIPT CODE
// jQuery 3.4.1


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

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

const locationURL = document.location.href;
const itemSlug = locationURL.substring(21,locationURL.length-1);

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


function makeCommentBoxHTML(data) {
    var html = '';
    html += '<div class=\"comment\" style=\"padding: 10px;\">';
    html += '<p class="font-weight-bold">';
    html += `${data.username} `;
    html += "<span class=\" text-muted font-weight-normal\">";
    html += `${data.time}`;
    html += "</span>";
    html += "</p>";
    html += `${data.textBody}`;
    html += '</div>';
    html += '</div>';
    return html
}

const monthNames = ["იან", "თებ", "მარ", "აპრ", "მაი", "ივნ",
    "ივლ", "აგვ", "სექ", "ოქტ", "ნოვ", "დეკ"
];

function convertTimeGeo(timestamp) {
    var date = new Date(timestamp*1000);
    date = `${date.getDay()} ${monthNames[date.getMonth()]} ${date.getFullYear()} ${date.getHours()}:${date.getMinutes()}`;
    return date;
}

var $commentForm = $('.comment-form');
$commentForm.submit(function(event){
    event.preventDefault();
    var $formDataSerialized = $(this).serialize();
    $.ajax({
        method: "POST",
        url: window.location.href+'comment/',
        data: $formDataSerialized,
        success: function (data) {
            data.textBody = $(".comment-form textarea").val();
            data.time = convertTimeGeo(new Date().getTime()/1000);
            var html =makeCommentBoxHTML(data);
            $(".comments-box").prepend(html);
            $commentForm.trigger('reset');
        },
        error: function (data) {
            console.log(data);
        },
    })
});

// function handleFormSuccess(data, textStatus, jqXHR){
//     console.log(data);
//     $commentForm.trigger('reset');
// }
//
// function handleFormError(jqXHR, textStatus, errorThrown){
//     console.log(jqXHR);
//     console.log(textStatus);
//     console.log(errorThrown)
// }
