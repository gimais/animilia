// jQuery 3.4.1

function escapeHTML(txt) {
    return txt
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/'/g, "&#039;")
         .replace(/"/g, "&quot;")
         .replace(/>/g, "&gt;");
}

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

var request_user_id = $('.top-nav li a[href="/account/profile/"]').data('id');

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


function makeCommentBoxHTML(data,reply=false) {
    var html = '';
    html += `<div class="comment${reply?' clearfix':''}">
                    <div class="comment-user-img" href="#user">
                        <img src="#" alt>
                    </div>
                    <div class="comment-body">
                        <div class="comment-info">
                            <p class='comment-user'>${escapeHTML(data.username)}</p>`;
    if(typeof request_user_id !== "undefined" && !data.deleted){
        html += `<p class="reply-button" data-it="${data.parent_id}" data-id="${data.comment_id}" data-username="${escapeHTML(data.username)}"><i class="fas fa-reply"></i>  პასუხი</p>`;
    }
    if (typeof request_user_id !== "undefined" && data.user_id===request_user_id && !data.deleted){
        if(data.dislikes === 0 && data.likes === 0) {
            html += `<div class="comment-right-buttons" id='edit-comment' style="color: #333333;"><i class="fas fa-edit"></i></div>`;}
         html += `<div class="comment-right-buttons" id='remove-comment' style="color: #333333;"><i class="fas fa-trash"></i></div>`;
    }
    if(!data.deleted){
        html += `<div class="comment-right-buttons" id='dislike-comment' style="color: #ab3717;"><i class="far fa-thumbs-down">${data.dislikes}</i></div>
                <div class="comment-right-buttons" id='like-comment' style="color: #ff2e01;" ><i class="far fa-thumbs-up"></i>${data.likes}</div>`
    }
        html+= `<p class='comment-time'>${convertTimeGeo(data.time)}</p>
            </div>`;
    if(data.deleted){
         html+= `<p style="border: 1px solid;text-align: center">ეს კომენტარი წაშლილია!</p>`
    }else{
        html+= `<p style="word-wrap: break-word;"">${escapeHTML(data.body)}</p>`
    }
    html+= `</div></div>`;
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
    textareObj.val(username+', ').focus();
    window.scroll({
        top: textareObj.offset().top - (screen.height/2),
        left: 0,
        behavior: 'smooth'
    });
}


function convertTimeGeo(date) {
    date = new Date(date*1000);
    date = `${(date.getDate()<10?'0':'') + date.getDate()}/${((date.getMonth()+1)<10?'0':'') + (date.getMonth()+1)}/${date.getFullYear()} | ${(date.getHours()<10?'0':'') + date.getHours()}:${(date.getMinutes()<10?'0':'') + date.getMinutes()}`;
    return date;
}

var $commentForm = $('.comment-form');
$commentForm.submit(function(event){
    event.preventDefault();
    var $formDataSerialized = $(this).serialize();
    $.ajax({
        method: "POST",
        url: window.location.origin+'/account/comment/',
        data: $formDataSerialized+'&id='+$('.item-page').data('id'),
        success: function (data) {
            data.body = $(".comment-form textarea").val();
            data.time = new Date().getTime()/1000;
            data.parent_id = data.comment_id;
            var html = makeCommentBoxHTML(data,true);
            $(".comments-box").prepend(html);
            $commentForm.trigger('reset');
        },
        error: function (data) {
            console.log(data);
        },
    })
});


$('.comments-box').on('click','.reply-button',function () {
    var button = $(this);
    var parent_id = button.data('it') || button.data('id');
    var username = button.data('username');
    var formHTML = makeCommentTextAreaHTML(parent_id);
    var lastComment = button.parents('.comment:last');
    if(lastComment.find('.comment-form').length===0){
        lastComment.append(formHTML)
    }
    var commentForm = lastComment.find('.comment-form');
    commentForm.find('textarea').val(username+', ').focus();
    var checkRepliesButton = lastComment.find('.comment-replies-check');
    if(checkRepliesButton.length === 1) {
        if(checkRepliesButton.hasClass('closed'))
            getChildComments(checkRepliesButton,parent_id);
    }
});

function getChildComments(that,parent_id,purpose=NaN,htmlcode=null,username=null){
    var commentClosed = that.text().replace('დამალვა','ჩვენება');
    var commentsOpened = that.text().replace('ჩვენება','დამალვა');
    if(!that.hasClass('done')){
        that.html('მოიცადეთ...');
        that.toggleClass('closed opened done');
        $.ajax({
        method: "GET",
        url: window.location.origin+'/account/check_comments/'+parent_id,
        data: {
            'skip':0,
        },
        success: function (data) {
            that.html(commentsOpened);
            data.time = convertTimeGeo(new Date().getTime()/1000);
            var html = '';

            for(let i=data.length-1;i>=0;i--)
              html += makeCommentBoxHTML(data[i]);

            that.parent().find('.comment-replies-box').append(html);
            that.parent().find('.comment-replies-box').show();
        },
        error: function (data) {
            console.log('error - pasuxebi am komentarze ar arsebobs',data);
        },
        complete:function () {
            if(that.parent().find('.comment-form').length){
                window.scroll({
                    top: that.parent().find('.comment-form textarea').offset().top - screen.height/2 + 50,
                    left: 0,
                    behavior: 'smooth'
                });
            }
        }
    }) // ajax end block
    }else{
        if(that.hasClass('opened')){
            that.html(commentClosed);
            that.parent().find('.comment-replies-box').hide(200);
        }else{
            that.html(commentsOpened);
            that.parent().find('.comment-replies-box').show(200);
        }
        that.toggleClass('opened closed')
    }
}

$('.comments-box').on('click','.comment-replies-check',function () {
    var that = $(this);
    getChildComments(that,that.data('id'));
});

$('.comments-box').on("click", ".comment .comment-form button[type=reset]", function(e) {
    e.preventDefault();
    $(this).parent().remove();
});


// GASASWOREBELI
$('.comments-box').on("click", ".comment .comment-form button[type=submit]", function(event) {
    event.preventDefault();
    var that = $(this).parent();
    var $formDataSerialized = that.serialize();
    $.ajax({
        method: "POST",
        url: window.location.origin+'/account/comment/',
        data: $formDataSerialized + `&parent_id=${that.data('id')}`,
        success: function (data) {
            data.body = that.find('textarea').val();
            data.time = new Date().getTime()/1000;
            data.parent_id = that.data('id');
            var html = '';
            if(that.parent().has('.comment-replies-box').length){
                html = makeCommentBoxHTML(data);
                that.parent().children('.comment-replies-box').append(html)
            }else {
                html+= `<div class="comment-replies-check closed" data-id="${that.data('id')}">
<!--                            <i class="fas fa-caret-down" aria-hidden="true"></i>-->
                            პასუხების ჩვენება (0)
                            </div>
                            <div class="comment-replies-box">`;
               // html += makeCommentBoxHTML(data);
               html += '</div>';
               that.parent().append(html);
            }
            var replies_box = that.parent().find('.comment-replies-check');

            replies_box.text(replies_box.text().replace(/\d+/g,parseInt(replies_box.text().match(/\d+/g))+1));

            if(replies_box.hasClass('closed'))
                getChildComments(replies_box,that.data('id'));

            that.remove();
        },
        error: function () {
            that.remove();
        },
    })
});

$('.comments-box').on('click','.comment #remove-comment',function () {
    var that = $(this);
    var id = that.parent().find('.reply-button').data('id');
    $.ajax({
        method: "POST",
        url: window.location.origin+'/account/comment/delete/',
        data: {id:id},
        success: function (data) {
            if(that.parents('.comment').attr('class')==='comment clearfix'){
                that.parents('.comment').fadeOut(300, function() { $(this).remove(); })
            }else{
                data.username = that.parent().find('.comment-user').text();
                data.deleted = true;
                data.time = new Date().getTime()/1000;
                that.closest('.comment').hide(100, function() { $(this).html(makeCommentBoxHTML(data)).show(200); })
            }
        },
        error: function (data) {
            console.log(data);
        },
    })
});

$('.comment').on('click','#edit-comment',function () {
    var that = $(this);
    alert('jer repliebia gasarkvevi!!')
    // var id = that.parent().find('.reply-button').data('id');
    // var commentBox = that.closest('.comment');
    // commentBox.find('.reply-button').hide();
    // commentBox.find('.comment-right-buttons').hide();
    // commentBox.find('p').hide();
    // $.ajax({
    //     method: "POST",
    //     url: window.location.origin+'/account/comment/edit/',
    //     data: {id:id},
    //     success: function (data) {
    //         // if(that.parents('.comment').attr('class')==='comment clearfix'){
    //         //     that.parents('.comment').fadeOut(300, function() { $(this).remove(); })
    //         // }else{
    //         //     data.username = that.parent().find('.comment-user').text();
    //         //     data.deleted = true;
    //         //     data.time = new Date().getTime()/1000;
    //         //     that.closest('.comment').hide(100, function() { $(this).html(makeCommentBoxHTML(data)).show(200); })
    //         // }
    //         alert('Sheicvala')
    //     },
    //     error: function (data) {
    //         console.log(data);
    //     },
    // })
});


$('.comment').on('click','#like-comment',function () {
    var that = $(this);
    var id = that.parent().find('.reply-button').data('id');
    $.ajax({
        method: "POST",
        url: window.location.origin+'/account/comment/like/',
        data: {id:id},
        success: function (data) {
            that.html(`<i class="fas fa-thumbs-up" aria-hidden="true"></i>`+(parseInt(that.text())+1));
        },
        error: function (data) {
            console.log(data);
        },
    })
});

$('.comment').on('click','#dislike-comment',function () {
    var that = $(this);
    var id = that.parent().find('.reply-button').data('id');
    $.ajax({
        method: "POST",
        url: window.location.origin+'/account/comment/dislike/',
        data: {id:id},
        success: function (data) {
            that.html(`<i class="fas fa-thumbs-down" aria-hidden="true"></i>`+(parseInt(that.text())+1));
        },
        error: function (data) {
            console.log(data);
        },
    })
});