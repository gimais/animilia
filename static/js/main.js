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
    html += `<div class="comment">
                    <div class="comment-user-img" href="#user">
                        <img src="#" alt>
                    </div>
                    <div class="comment-body">
                        <div class="comment-info">
                            <p class='comment-user'>${data.username}</p>
                            <p class="reply-button" data-id="${data.parent_id}" data-username="${data.username}"><i class="fas fa-reply"></i>  პასუხი</p>
                            <p class='comment-time'>${convertTimeGeo(data.time)}</p>
                        </div>
                            <p style="word-wrap: break-word">${data.body}</p>
                    </div>
                </div>`;
    return html
}

function makeCommentTextAreaHTML(parent_id){
    var html = '';
    html += `<form class=\'comment-form\' style=\'padding: 15px 0\' method=\'POST\' data-id=\"${parent_id}\">`;
    html += `<input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">`;
    html += '<p> <textarea name="body" cols="40" rows="10" placeholder="კომენტარი" id="id_body"></textarea></p>';
    html += '<button type="submit">გაგზავნა</button>';
    html += '<button type="reset">გაუქმება</button>';
    html += '</form>';
    return html
}

function makeTextarea(textareObj,username){
    textareObj.val(username+', ');
    textareObj.trigger('focus');
}

function convertTimeGeo(date) {
    date = new Date(date*1000);
    date = `${date.getDate()}/${date.getMonth()}/${date.getFullYear()} | ${(date.getHours()<10?'0':'') + date.getHours()}:${(date.getMinutes()<10?'0':'') + date.getMinutes()}`;
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
            data.body = $(".comment-form textarea").val();
            data.time = new Date().getTime()/1000;
            var html = makeCommentBoxHTML(data);
            $(".comments-box").prepend(html);
            $commentForm.trigger('reset');
        },
        error: function (data) {
            console.log(data);
        },
    })
});


$(".comment").on('click','.reply-button',function () {
    var button = $(this);
    var parent_id = button.data('id');
    var username = button.data('username');
    var formHTML = makeCommentTextAreaHTML(parent_id);
    var parent = button.parents('.comment:last');
    if(parent.find('.comment-form').length===0){
        var reply_button = parent.find('.comment-replies-check');
        if(reply_button.length === 1) {
            if (reply_button.hasClass('done')) {
                if (reply_button.hasClass('closed')) {getChildComments(reply_button,parent_id)}
                parent.append(formHTML);
                makeTextarea(parent.find('.comment-form textarea'),username)
            } else
                getChildComments(reply_button,parent_id,1,formHTML,username);
        } else {
            parent.append(formHTML);
            makeTextarea(parent.find('.comment-form textarea'),username);
        }
    } else {
        makeTextarea(parent.find('.comment-form textarea'),username);
    }
});

function getChildComments(that,parent_id,purpose=0,htmlcode=null,username=null){
    var commentClosed = '<i class="fas fa-caret-down"></i>'+that.text().replace('დამალვა','ჩვენება');
    var commentsOpened = that.text().replace('ჩვენება','დამალვა') +'<i class="fas fa-caret-up"></i>';
    if(!that.hasClass('done')){
        that.html('მოიცადეთ...');
        that.toggleClass('closed opened done');
        $.ajax({
        method: "GET",
        url: window.location.origin+'/anime/check_comments/'+parent_id,
        data: {
            'skip':0,
        },
        success: function (data) {
            that.html(commentsOpened);
            data.time = convertTimeGeo(new Date().getTime()/1000);
            var html = '';
            if(!that.parent().has('.comment-replies-box').length){
               html += '<div class="comment-replies-box">';
               for(let i=data.length-1;i>=0;i--){
                  html += makeCommentBoxHTML(data[i]);
               }
               html += '</div>';
                that.parent().append(html);
                if(purpose){
                    that.parent().append(htmlcode);
                    makeTextarea(that.parent().find('.comment-form textarea'),username);
                }
            }
        },
        error: function (data) {
            console.log('error - pasuxebi am komentarze ar arsebobs',data);
        },
    })
    }else{
        if(that.hasClass('opened')){
            that.html(commentClosed);
            that.parent().find('.comment-replies-box').hide();
        }else{
            that.html(commentsOpened);
            that.parent().find('.comment-replies-box').show();
        }
        that.toggleClass('opened closed')
    }
}


$('.comment').on("click", ".comment-form button[type=reset]", function() {
    $(this).parent().remove();
});

$('.comment').on("click", ".comment-form button[type=submit]", function(event) {
    event.preventDefault();
    var that = $(this).parent();
    var $formDataSerialized = that.serialize();
    $.ajax({
        method: "POST",
        url: window.location.href+'comment/',
        data: $formDataSerialized + `&parent_id=${that.data('id')}`,
        success: function (data) {
            data.body = that.find('textarea').val();
            data.time = new Date().getTime()/1000;
            var html = '';
            if(that.parent().has('.comment-replies-box').length){
                html = makeCommentBoxHTML(data);
                that.parent().children('.comment-replies-box').append(html)
            }else {
               html += '<div class="comment-replies-box">';
               html += makeCommentBoxHTML(data);
               html += '</div>';
               that.parent().append(html);
            }
            var replies_box = that.parent().find('.comment-replies-check');
            if(replies_box.hasClass('closed'))
                getChildComments(replies_box,that.data('id'));
            that.remove();
        },
        error: function (data) {
            console.log(data);
        },
    })
});

$('.comment-replies-check').on('click',function () {
    var that = $(this);
    getChildComments(that,that.data('id'));
});