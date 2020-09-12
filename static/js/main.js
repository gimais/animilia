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

function activateClassButton(button){
       var activatedButton = $('.item-page-episodes').find('.episode-select-button.active');
       if(button!==activatedButton) {
               activatedButton.removeClass('active');
               button.addClass('active');
       }
}

const cT = function () {
    var date = new Date();
    return date.getTime()
};

function setCookie(name, value, expire) {
        var date = new Date();
        date.setTime(date.getTime() + (expire*24*60*60*1000));
        var expires = "expires="+ date.toUTCString();
        document.cookie = name + "=" + value + ";" + expires ;
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

const itemSlug = document.location.pathname;

$('.episode-select-button').on('click',function () {
        var clickedButton = $(this);
        activateClassButton(clickedButton);
        var videoURL = clickedButton.data('url');
        $('.item-player iframe').attr('src',videoURL);
        if ($('.item-player').hasClass('hidden')) {
                $('.item-player').removeClass('hidden');
        }
        setCookie(itemSlug.substring(7,itemSlug.length-1),clickedButton.data('id'),20);
});


function makeCommentBoxHTML(data,reply=false) {
    var html = '';
    html += `<div class="comment${reply?' clearfix':''}">
                    <a class="comment-user-img" href="/profile/${data.user_id}">
                        <img src=${window.location.origin+'/media/'+data.avatar} alt>
                    </a>
                    <div class="comment-body">
                        <div class="comment-info">`;

    if(data.user_id === request_user_id){
        html += `<a class='comment-user mine' href="/profile/${data.user_id}">${escapeHTML(data.username)}</a>`;
    }else{
        html += `<a class='comment-user' href="/profile/${data.user_id}">${escapeHTML(data.username)}</a>`;
    }

    if(typeof request_user_id !== "undefined" && !data.deleted){
        html += `<p class="reply-button" data-it="${data.parent_id?data.parent_id:data.comment_id}" data-id="${data.comment_id}" data-username="${escapeHTML(data.username)}"><i class="fas fa-reply"></i>  პასუხი</p>`;
    }
    if (typeof request_user_id !== "undefined" && data.user_id===request_user_id && !data.deleted){
        if(typeof data.dislikes === "undefined" && typeof data.likes === "undefined" || data.dislikes ===0 && data.likes === 0) {
            html += `<div class="comment-right-buttons" id='edit-comment' style="color: #333333;"><i class="fas fa-edit"></i></div>`;
        }
         html += `<div class="comment-right-buttons" id='remove-comment' style="color: #333333;"><i class="fas fa-trash"></i></div>`;
    }
    if(!data.deleted){
        html += `<div class="comment-dl-buttons">
                    <div class="comment-right-buttons" id='dislike-comment' style="color: #ab3717;"><i class="fa${data.voted === 1 ? 's' : 'r'} fa-thumbs-down"></i>${data.dislikes ? data.dislikes : 0}</div>
                    <div class="comment-right-buttons" id='like-comment' style="color: #ff2e01;" ><i class="fa${data.voted === 0 ? 's' : 'r'} fa-thumbs-up"></i>${data.likes ? data.likes : 0}</div>
                </div>`;
    }
        html+= `<p class='comment-time'>${convertTimeGeo(data.time)}</p>
            </div>`;
    if(data.deleted){
        html+= `<p class="deleted-comment">ეს კომენტარი წაშლილია!</p>`
    }else{
        html += `<p style="word-wrap: break-word;"">${ifCommentContainsSpoiler(escapeHTML(data.body))}</p>`
    }
    html+= '</div>';

    if(typeof data.childs_count !== "undefined" && data.childs_count > 0) {
        html += `<div class="comment-replies-check closed" data-id="${data.comment_id}">
                პასუხების ჩვენება (${data.childs_count})
            </div>
                <div class="comment-replies-box" style="display: none"></div>`;
    }

    html += '</div>';
    return html
}

function makeCommentTextAreaHTML(parent_id){
    var html = '';
    html += `<form class=\'comment-form\' style=\'padding: 15px 0\' method=\'POST\' data-id=\"${parent_id}\">
            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
            <p> <textarea name="body" cols="40" rows="10" placeholder="კომენტარი" id="id_body"></textarea></p>
            <button class="spoiler-button">სპოილერი</button>
            <button type="submit">გაგზავნა</button>
            <button type="reset">გაუქმება</button>
            </form>`;
    return html
}

function makeTextareaEdit(parent_id,spoiler){
    var html = '';
    html += `<form class=\'comment-edit-form\' style=\'padding: 15px 0\' method=\'POST\' data-id=\"${parent_id}\">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                <p><textarea name="body" cols="40" rows="10" placeholder="კომენტარი" id="id_body"></textarea></p>
                <button class="spoiler-button" ${spoiler? 'disabled' : ''}>სპოილერი</button>
                <button type="submit">შეცვლა</button>
                <button type="reset">გაუქმება</button>
                </form>`;
    return html
}

function getChildComments(that,parent_id,replying=false,more=0){
    var commentClosed = that.text().replace('დამალვა','ჩვენება');
    var commentsOpened = that.text().replace('ჩვენება','დამალვა');
    if(!that.hasClass('done') || more){
        that.html('მოიცადეთ...');
        that.toggleClass('closed opened done');
        $.ajax({
        method: "GET",
        url: window.location.origin+'/account/check_replies/'+parent_id,
        data: {
            'skip': 1,
        },
        success: function (data) {
            that.html(commentsOpened);
            data.time = convertTimeGeo(new Date().getTime()/1000);
            var html = '';

            for(let i=data.length-1;i>=0;i--)
              html += makeCommentBoxHTML(data[i]);

            that.parent().find('.comment-replies-box').append(html);
            if(replying)
                that.parent().find('.comment-replies-box').show();
            that.parent().find('.comment-replies-box').show(200);
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

function convertTimeGeo(date) {
    date = new Date(date*1000);
    date = `${(date.getDate()<10?'0':'') + 
    date.getDate()}/${((date.getMonth()+1)<10?'0':'') + 
    (date.getMonth()+1)}/${date.getFullYear()} | ${(date.getHours()<10?'0':'') + 
    date.getHours()}:${(date.getMinutes()<10?'0':'') + date.getMinutes()}`;
    return date;
}

var $commentForm = $('.comment-form');
$commentForm.submit(function(event){
    event.preventDefault();
    var $formDataSerialized = $(this).serialize();
    var textArea = $(this).find('textarea').val();

    if(!checkCommentContainsMoreSpoilers(textArea)) {
        $.ajax({
            method: "POST",
            url: window.location.origin + '/account/comment/',
            data: $formDataSerialized + '&id=' + $('.item-page').data('id'),
            success: function (data) {
                data.body = $(".comment-form textarea").val();
                data.time = new Date().getTime() / 1000;
                data.parent_id = data.comment_id;
                var html = makeCommentBoxHTML(data, true);

                $(".comments-box").prepend(html);
                $(".comments-box > .comment:first").hide(10).show(100);
                $commentForm.trigger('reset')
                $('.spoiler-button').attr('disabled',false);
            },
            error: function (data) {
                console.log(data);
            },
        })
    }else
        alert('გთხოვთ, გამოიყენოთ მხოლოდ 1 სპოილერი!')
});

function ifCommentContainsSpoiler(text) {
    while(text.includes('[spoiler]')) {
        text = spoilerAlertBBToHTML(text);
    }
    return text
}

function checkCommentContainsMoreSpoilers(text) {
    return text.indexOf('[spoiler]') !== text.lastIndexOf('[spoiler]');
}

function spoilerAlertBBToHTML($str) {
    $format_search = /\[spoiler\](.*?)\[\/spoiler\]/ig;
    $format_replace = '<span class="spoiler">$1</span><button id="reveal-spoiler">სპოილერი</button>';

    return $str.replace($format_search, $format_replace);
}

function spoilerALertHTMLToBB(text) {
    while(text.includes('<span')) {
        text = text.replace(/<span (.*?)>(.*?)<\/span>/gi, "[spoiler]$2[/spoiler]");
        text = text.replace(/<button (.*?)>(.*?)<\/button>/gi,'');
    }
    return text
}

$('.comments-box, .comment-form').on('click','.reply-button',function () {
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
            getChildComments(checkRepliesButton,parent_id,true);
    }
}).on('click','.comment-replies-check',function () {
    var that = $(this);
    getChildComments(that,that.data('id'));
}).on("click", ".comment .comment-form button[type=reset]", function(e) {
    e.preventDefault();
    $(this).parent().remove();
}).on("click", ".comment .comment-form button[type=submit]", function(event) {
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
                that.parent().find('#edit-comment').remove();
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
}).on('click','.comment #remove-comment',function () {
    if(confirm('დარწმუნებული ხართ, რომ კომენტარის წაშლა გინდათ? ამ ქმედების შემდეგ კომენტარს ვეღარ აღადგენთ.')) {
        var that = $(this);
        var id = that.parent().find('.reply-button').data('id');
        $.ajax({
            method: "POST",
            url: window.location.origin + '/account/comment/delete/',
            data: {id: id},
            success: function (data) {
                if (that.parents('.comment').attr('class') === 'comment clearfix') {
                    that.parents('.comment').fadeOut(300, function () {
                        $(this).remove();
                    })
                } else {
                    var comment_box =  that.closest('.comment');
                    data.username = that.parent().find('.comment-user').text();
                    data.deleted = true;
                    data.time = new Date().getTime() / 1000;
                    data.avatar = comment_box.find('img').attr('src').match(/[\w-]+\.jpg/g);
                    if(!(data.avatar == 'no-avatar.jpg')) {
                        data.avatar = 'avatars/' + data.avatar;
                    }
                    comment_box.hide(100, function () {
                        $(this).html(makeCommentBoxHTML(data)).show(200);
                    })
                }
            },
            error: function (data) {
                console.log(data);
            },
        })
    }
}).on('click','.comment #edit-comment',function () {
    var that = $(this);
    var id = that.parent().find('.reply-button').data('id');
    var commentBox = that.closest('.comment');
    var hasSpoiler = that.parent().next().find('span').length > 0;

    that.hide();
    commentBox.find('.reply-button:first').hide();
    commentBox.find('#like-comment:first').hide();
    commentBox.find('#remove-comment:first').hide();
    commentBox.find('#dislike-comment:first').hide();
    var textareaValue = spoilerALertHTMLToBB(commentBox.find('p:not([class])').html());

    commentBox.find('p:not([class])').hide();
    commentBox.append(makeTextareaEdit(id,hasSpoiler));
    commentBox.find('.comment-edit-form textarea').focus().val(textareaValue);
}).on('click','.comment .comment-edit-form button[type=reset]',function (e) {
    e.preventDefault();
    var parent = $(this).parent();
    parent.parent().find('*').show();
    $(parent).prev().find('#reveal-spoiler').hide();
    parent.remove();
}).on('click','.comment .comment-edit-form button[type=submit]',function (e) {
    e.preventDefault();
    var parent = $(this).parent();
    var finText = parent.find('textarea').val();

    if(spoilerALertHTMLToBB(parent.prev().find('p')[2].innerHTML) !== finText){
        var $formSerialized = parent.serialize();

        $.ajax({
            method: "POST",
            url: window.location.origin + '/account/comment/edit/',
            data: $formSerialized + '&id=' + parent.data('id'),
            success: function (data) {
                parent.parent().find('p:not([class])').text(finText);
                parent.parent().find('.comment-time').text(convertTimeGeo(data.time));
                parent.parent().find('*').show();
                parent.remove();
            },
            error: function () {
                parent.parent().find('*').show();
                parent.remove();
            },
        })
    }else{
        alert('შეცვლა არ მოხდა, რადგან ტექსტი არ შეცვლილა!')
    }
}).on('click','#like-comment',function () {
    var that = $(this);
    var parent = $(this).parent().parent();

    if (!parent.find('.comment-user').hasClass('mine')) {
        var id = parent.find('.reply-button').data('id');
        $.ajax({
            method: "POST",
            url: window.location.origin + '/account/comment/like/',
            data: {id: id},
            success: function (data) {
                if (data.type===1) {
                    that.hide(100, function() {
                        $(this).html(`<i class="fas fa-thumbs-up" aria-hidden="true"></i>` + (parseInt(that.text()) + 1)).show(200);
                    })
                }
                else if(data.type === 0)
                    that.hide(100, function() {
                        $(this).html(`<i class="far fa-thumbs-up" aria-hidden="true"></i>` + (parseInt(that.text()) - 1)).show(200);
                    });
                else if(data.type === 2){
                    parent.find('#dislike-comment').hide(100, function () {
                        $(this).html(`<i class="far fa-thumbs-down" aria-hidden="true"></i>` + (parseInt(that.parent().find('#dislike-comment').text()) - 1)).show(200);
                    });
                    that.hide(100, function() {
                        $(this).html(`<i class="fas fa-thumbs-up" aria-hidden="true"></i>` + (parseInt(that.text()) + 1)).show(200);
                    })
                }
            },
            error: function (data) {
                console.log(data);
            },
        })
    }else
        alert('საკუთარი კომენტარის დალაიქება არ მოსულა!')
}).on('click','#dislike-comment',function () {
    var that = $(this);
    var parent = $(this).parent().parent();
    if (!parent.find('.comment-user').hasClass('mine')) {
        var id = parent.find('.reply-button').data('id');
        $.ajax({
            method: "POST",
            url: window.location.origin + '/account/comment/dislike/',
            data: {id: id},
            success: function (data) {
                if (data.type===1)
                    that.hide(100, function () {
                        $(this).html(`<i class="fas fa-thumbs-down" aria-hidden="true"></i>` + (parseInt(that.text()) + 1)).show(200);
                    });
                else if(data.type===0)
                    that.hide(100, function () {
                        $(this).html(`<i class="far fa-thumbs-down" aria-hidden="true"></i>` + (parseInt(that.text()) - 1)).show(200);
                    });
                else if(data.type === 2){
                    parent.find('#like-comment').hide(100, function () {
                        $(this).html(`<i class="far fa-thumbs-up" aria-hidden="true"></i>` + (parseInt(that.parent().find('#like-comment').text()) - 1)).show(200);
                    });
                    that.hide(100, function() {
                        $(this).html(`<i class="fas fa-thumbs-down" aria-hidden="true"></i>` + (parseInt(that.text()) + 1)).show(200);
                    })
                }
            },
            error: function (data) {
                console.log(data);
            },
        })
    }else
        alert('რა იყო პიროვნების გაორება გაქვს?')
}).on('click','.spoiler-button',function (e) {
    e.preventDefault();
    var tx = $(this).parent().find('textarea')[0];
    var start = tx.selectionStart;
    var end = tx.selectionEnd;
    var sel = tx.value.substring(start, end);
    tx.value = tx.value.substring(0, start) + '[spoiler]' + sel + '[/spoiler]' + tx.value.substring(end);
    tx.focus();
    tx.selectionEnd= end + 9;
    $(this).attr('disabled',true);
}).on('click','#reveal-spoiler',function (e) {
    e.stopPropagation();
    $(this).prev().fadeIn();
    $(this).hide();
}).on('click','.spoiler',function (e) {
    e.stopPropagation();
    $(this).next().fadeIn();
    $(this).hide();
}).on('keyup','textarea',function (e) {
    if(!$(this).val().length)
        $(this).parent().next().removeAttr('disabled');
});

$('.showmore').on('click',function () {
    var that = $(this);
    var current_page = parseInt(that.attr('data-page'));
    $.ajax({
        method: "GET",
        url: window.location.origin+'/anime/more_comments/',
        data: {
            'skip': current_page+1,
            'id':$('.item-page').data('id'),
        },
        success: function (data) {
            var html = '';
            for(let i=0;i<data.length;i++)
              html += makeCommentBoxHTML(data[i],true);
            that.attr('data-page',current_page+1);
            $('.comments-box').append(html);
            if(that.attr('data-max') == current_page+1){
                that.remove();
            }
        },
        error: function () {
            console.log('meti comment ar aris');
        },
    })
});


function getYearsSelectOptionsHTML(startYear,EndYear) {
    var html = '';
    for(let i=EndYear;i>=startYear;i--){
       html += '<option value="' + i + '">' + i + '</option>';
    }
    return html
}

function getMonthsSelectOptionsHTML() {
    const monthNames = [ "იანვარი", "თებერვალი", "მარტი", "აპრილი", "მაისი", "ივნისი",
                        "ივლისი", "აგვისტო", "სექტემბერი", "ოქტომბერი", "ნოემბერი", "დეკემბერი"];
    var html = "";
    for (let i = 1; i <= monthNames.length; i++) {
        html += '<option value="' + i + '">' + monthNames[i-1] + '</option>';
    }
    return html
}

function getDaysSelectOptionsHTML(days) {
    var html = '';
    for(let i=1;i<=days;i++){
       html += '<option value="' + i + '">' + i + '</option>';
    }
    return html
}

$('.profile-edit button[type=submit]').on('click',function (e) {
    e.preventDefault();
    var selectedDay = parseInt($("select[name='birth-day'] option:selected").val());
    var selectedMon = parseInt($("select[name='birth-month'] option:selected").val());
    var selectedYea = parseInt($("select[name='birth-year'] option:selected").val());
    if(selectedDay!==0 && selectedMon !== 0 && selectedYea !== 0)
        $('input[name=birth]').val(selectedYea+'-'+selectedMon+'-'+selectedDay);
    else
        $('input[name=birth]').val(null);

    $('.profile-details').submit();
});


$('.profile-details-input').on('click','#change-username-button',function (e) {
    e.preventDefault();
    var that = $(this);
    var parent = that.parent();
    var inputEl = parent.find('input');
    var username = inputEl.val();
    that.css('background-color','#333');
    inputEl.attr('readonly',null);
    inputEl.css('background-color','#FFF');
    inputEl.focus().val('').val(username);
    that.text('დადასტურება');
    parent.append(`<button type="reset" class="cancel">გაუქმება</button>`);
    that.attr('id','submit-username-button');
}).on('click','.cancel',function (e) {
    e.preventDefault();
    var that = $(this);
    var parent = that.parent();
    var inputEl = parent.find('input');
    var submitButton = parent.find('#submit-username-button');
    inputEl.attr('readonly','');
    inputEl.css('background-color','#aaaa');
    inputEl.val($('a[href="/account/profile/"]').text());
    submitButton.text('შეცვლა');
    submitButton.attr('id','change-username-button');
    that.remove();
}).on('click','#change-email-button',function (e) {
    e.preventDefault();
    $.ajax({
        method: "GET",
        url: window.location.origin + '/account/email_change/',
        success: function () {
            alert('მოთხოვნა გაიგზავნა თქვენს Email-ზე,გთხოვთ გადაამოწმოთ! შეამოწმეთ Spam ფაილიც!')
        },
        error: function () {
            alert('მოხდა შეცდომა! თავიდან სცადეთ!');
        }
    });
});