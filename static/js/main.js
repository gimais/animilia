// jQuery 3.4.1
"use strict";

const itemSlug = document.location.pathname;
const request_user_id = $('.top-nav li a[href="/account/profile/"]').data('id');

function escapeHTML(txt) {
    return txt
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/'/g, "&#039;")
        .replace(/"/g, "&quot;")
        .replace(/>/g, "&gt;");
}

function newLineToBr(txt) {
    return txt.replace(/(?:\r\n|\r|\n)/g, '<br>');
}

function brToNewLine(text) {
    return text.replace(/<br\s*[\/]?>/gi, "\n");
}

function cT() {
    return new Date().getTime()
}

function convertTimeGeo(date) {
    date = new Date(date * 1000);
    date = `${(date.getDate() < 10 ? '0' : '') +
    date.getDate()}/${((date.getMonth() + 1) < 10 ? '0' : '') +
    (date.getMonth() + 1)}/${date.getFullYear()} | ${(date.getHours() < 10 ? '0' : '') +
    date.getHours()}:${(date.getMinutes() < 10 ? '0' : '') + date.getMinutes()}`;
    return date;
}

function getYearsSelectOptionsHTML(startYear, EndYear) {
    let html = '';
    for (let i = EndYear; i >= startYear; i--) {
        html += '<option value="' + i + '">' + i + '</option>';
    }
    return html
}

function getMonthsSelectOptionsHTML() {
    const monthNames = ["იანვარი", "თებერვალი", "მარტი", "აპრილი", "მაისი", "ივნისი",
        "ივლისი", "აგვისტო", "სექტემბერი", "ოქტომბერი", "ნოემბერი", "დეკემბერი"];
    let html = "";

    for (let i = 1; i <= monthNames.length; i++) {
        html += '<option value="' + i + '">' + monthNames[i - 1] + '</option>';
    }
    return html
}

function getDaysSelectOptionsHTML(days) {
    let html = '';
    for (let i = 1; i <= days; i++) {
        html += '<option value="' + i + '">' + i + '</option>';
    }
    return html
}

function setCookie(name, value, expire) {
    let date = new Date();
    date.setTime(date.getTime() + (expire * 24 * 60 * 60 * 1000));
    let expires = "expires=" + date.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=" + window.location.pathname;
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

function validateComment(text) {
    if (text.length < 6)
        return 'კომენტარი მინიმუმ 6 სიმბოლოსგან უნდა შედგებოდეს';
    else if (text.length > 4000)
        return 'კომენტარი მაქსიმუმ 4000 სიმბოლოსგან უნდა შედგებოდეს';
    else if (text.indexOf('[spoiler]') !== text.lastIndexOf('[spoiler]'))
        return "გთხოვთ, გამოიყენოთ მხოლოდ 1 სპოილერი.";
    else if (text.match(/\[spoiler\](.*?)\[\/spoiler\]/ig) !== null)
        if (text.match(/\[spoiler\](.*?)\[\/spoiler\]/ig)[0].length < 21)
            return "სპოილერი მინიმუმ 2 სიმბოლოსგან უნდა შედგებოდეს.";
    return null;
}

function HTMLToBB(text) {
    while (text.includes('class="spoiler"')) {
        text = text.replace(/<span (.*?)>(.*?)<\/span>/gi, "[spoiler]$2[/spoiler]");
        text = text.replace(/<button (.*?)>(.*?)<\/button>/gi, '');
    }

    while (text.match(/\<a[^>]+href=\"(.*?)\"[^>]*>(.*?)<\/a>/g) != null)
        text = text.replace(/\<a[^>]+href=\"(.*?)\"[^>]*>(.*?)<\/a>/g, "[url=$1]$2[/url]");

    return brToNewLine(text);
}

function BBtoHTML(text) {
    while (text.match(/\[url=(.*?)\](.*?)\[\/url\]/ig) != null)
        text = text.replace(/\[url=(http[s]?:\/\/)?(.*?)\](.*?)\[\/url\]/ig, '<a href="http://$2" rel="nofollow" target="_blank">$3</a>');


    while (text.match(/\[spoiler\](.*?)\[\/spoiler\]/ig) != null)
        text = text.replace(/\[spoiler](.*?)\[\/spoiler]/ig, '<span class="spoiler">$1</span><button id="reveal-spoiler">სპოილერი</button>');

    return text;
}

function readMoreComment(text) {
    if (text.height() > 72) {
        text.addClass('hide-this');
        text.after('<button class="read-more">სრულად</button>')
    }
}

function makeCommentTextHTML(body) {
    return BBtoHTML(newLineToBr(escapeHTML(body)));
}

function makeCommentBoxHTML(data) {
    let html = '';
    html += `<div class="comment clearfix">
                    <a class="comment-user-img" href="/profile/${data['user_id']}/">
                        <img src=${'/media/' + data.avatar} alt="avatar" loading="lazy">
                    </a>
                    <div class="comment-body">
                        <div class="comment-info" data-id="${data['comment_id']}">
                            <a class='comment-user${data['user_id'] === request_user_id ? " mine" : ""}' href="/profile/${data['user_id']}/">${data.username}</a>`;

    if (!data['user_active']) {
        html += `<span class="banned"> BANNED</span>`;
    }

    if (typeof request_user_id !== "undefined" && data['user_active'])
        html += `<p class="reply-button" data-id="${data['comment_id']}" data-username="${data.username}">
                            <i class="fas fa-reply"></i> პასუხი
                        </p>`;

    html += `<p class='comment-time'>${convertTimeGeo(data.time)}</p>
                        </div>
                        <p class="comment-text">${makeCommentTextHTML(data.body)}</p>
                        <div class="comment-actions">
                            <div class="comment-dl-buttons">
                                <div class="comment-right-buttons" id='like-comment' style="color: #ff2e01;" >
                                    <i class="fa${data['voted'] === 0 ? 's' : 'r'} fa-thumbs-up"></i>${data['likes']}
                                </div>
                                <div class="comment-right-buttons" id='dislike-comment' style="color: #ab3717;margin-right: 3px;">
                                    <i class="fa${data['voted'] === 1 ? 's' : 'r'} fa-thumbs-down"></i>${data['dislikes']}
                                </div>
                            </div>`;

    if (typeof request_user_id !== "undefined") {
        html += `<div class="user-actions">`;

        if (data['user_id'] === request_user_id) {
            if (data['dislikes'] === 0 && data['likes'] === 0) {
                html += `<div class="comment-right-buttons" id='edit-comment' style="margin-right: 3px;"><i class="fas fa-edit"></i></div>`;
            }
            html += `<div class="comment-right-buttons" id='remove-comment'><i class="fas fa-trash"></i></div>`;
        }
        if(data['user_active']){
                    html += `<p class="reply-button touch" data-id="${data['comment_id']}" data-username="${data.username}">
                        <i class="fas fa-reply"></i>  პასუხი
                </p>`;
        }
        html += `</div>`;
    }

    html += `</div></div>`;

    if (data['active_children_count'] > 0) {
        html += `<div class="comment-replies-check closed" data-id="${data['comment_id']}">
                    პასუხების ჩვენება (${data['children_count']})
                </div>
                <div class="comment-replies-box"></div>`;
    }

    html += `</div>`;

    return html
}

function makeReplyCommentBoxHTML(data) {
    let html = '';
    html += `<div class="comment">
                    <a class="comment-user-img" href="/profile/${data['user_id']}/">
                        <img src=${'/media/' + data.avatar} alt="avatar" loading="lazy">
                    </a>
                    <div class="comment-body">
                        <div class="comment-info" data-id="${data['comment_id']}">
                            <a class='comment-user${data['user_id'] === request_user_id ? " mine" : ""}' href="/profile/${data['user_id']}/">${data.username} </a>`;

    if (!data['user_active']) {
        html += `<span class="banned"> BANNED</span>`;
    }

    if (typeof request_user_id !== "undefined" && data['user_active'])
        html += `<p class="reply-button" data-it="${data.parent_id}" data-id="${data['comment_id']}" data-username="${data.username}">
                            <i class="fas fa-reply"></i> პასუხი
                </p>`;

    html += `<p class='comment-time'>${convertTimeGeo(data.time)}</p>
                        </div>
                        <p class="comment-text">${makeCommentTextHTML(data.body)}</p>
                        <div class="comment-actions">
                            <div class="comment-dl-buttons">
                                <div class="comment-right-buttons" id='like-comment' style="color: #ff2e01;" >
                                    <i class="fa${data['voted'] === 0 ? 's' : 'r'} fa-thumbs-up"></i>${data['likes']}
                                </div>
                                <div class="comment-right-buttons" id='dislike-comment' style="color: #ab3717;margin-right: 3px;">
                                    <i class="fa${data['voted'] === 1 ? 's' : 'r'} fa-thumbs-down"></i>${data['dislikes']}
                                </div>
                            </div>`;

    if (typeof request_user_id !== "undefined") {
        html += `<div class="user-actions">`;

        if (data['user_id'] === request_user_id) {
            if (data['dislikes'] === 0 && data['likes'] === 0) {
                html += `<div class="comment-right-buttons" id='edit-comment' style="margin-right: 3px"><i class="fas fa-edit"></i></div>`;
            }
            html += `<div class="comment-right-buttons" id='remove-comment'><i class="fas fa-trash"></i></div>`;
        }
        if (data['user_active']) {
            html += `<p class="reply-button touch" data-it="${data.parent_id}" data-id="${data['comment_id']}" data-username="${data.username}">
                        <i class="fas fa-reply"></i>  პასუხი
                </p>`;
        }
    }

    html += `</div></div></div>`;

    return html
}


function makeDeletedCommentBoxHTML(data) {
    let html = '';
    html += `<div class="comment ${data['active_children_count'] ? 'clearfix' : ''}">
                    <a class="comment-user-img" href="/profile/${data['user_id']}/">
                        <img src=${'/media/' + data.avatar} alt="avatar" loading="lazy">
                    </a>
                    <div class="comment-body">
                        <div class="comment-info" data-id="${data['comment_id']}">
                            <a class='comment-user' href="/profile/${data['user_id']}/">${data.username}</a>`;
    if (!data['user_active']) {
        html += `<span class="banned"> BANNED</span>`;
    }
    html += `<p class='comment-time'>${convertTimeGeo(data.time)}</p>
                        </div>
                            <p class="deleted-comment">ეს კომენტარი წაშლილია</p>
                    </div>`;

    if (typeof data['active_children_count'] !== "undefined" && data['active_children_count'] > 0) {
        html += `<div class="comment-replies-check closed" data-id="${data['comment_id']}">
                    პასუხების ჩვენება (${data['children_count']})
                </div>
                <div class="comment-replies-box"></div>`;
    }
    html += `</div>`;
    return html
}

function makeCommentTextAreaHTML(parent_id, replying_to_id = NaN) {
    let html = '';
    if (isNaN(replying_to_id)) {
        html += `<form class=\'comment-form\' style=\'padding: 15px 0\' data-id=\"${parent_id}\">`;
    } else {
        html += `<form class=\'comment-form\' style=\'padding: 15px 0\' data-id=\'${parent_id}\' data-it=\"${replying_to_id}\">`;
    }
    html += `<p> <textarea name="body" cols="40" rows="10" placeholder="კომენტარი" id="id_body"></textarea></p>
            <button class="spoiler-button">სპოილერი</button>
            <button type="submit">გაგზავნა</button>
            <button type="reset">გაუქმება</button>
            </form>`;
    return html
}

function makeEditTextarea(parent_id, spoiler) {
    let html = '';
    html += `<form class=\'comment-edit-form\' style=\'padding: 15px 0\' method=\'POST\' data-id=\"${parent_id}\">
                <p><textarea name="body" cols="40" rows="10" placeholder="კომენტარი" id="id_body"></textarea></p>
                <button class="spoiler-button" ${spoiler ? 'disabled' : ''}>სპოილერი</button>
                <button type="submit">შეცვლა</button>
                <button type="reset">გაუქმება</button>
            </form>`;
    return html
}

function getChildComments(that, parent_id, replying = false) {
    const commentClosed = that.text().replace('დამალვა', 'ჩვენება');
    const commentsOpened = that.text().replace('ჩვენება', 'დამალვა');

    if (!that.hasClass('done')) {
        that.html('მოიცადეთ...');
        that.toggleClass('closed opened');

        $.ajax({
            method: "GET",
            url: '/account/check_replies/' + parent_id,
            data: {
                'skip': 1,
            },
            success: function (e) {
                let commentRepliesBox = that.next('.comment-replies-box');
                let data = e['replies'];

                that.addClass('done');

                for (let i = data.length - 1; i >= 0; i--) {
                    if (typeof data[i].deleted === "undefined") {
                        commentRepliesBox.append(makeReplyCommentBoxHTML(data[i]));
                        readMoreComment(commentRepliesBox.find('.comment:last').find(".comment-text"));
                    } else
                        commentRepliesBox.append(makeDeletedCommentBoxHTML(data[i]));
                }

                if (e['availablePages'] > 1) {
                    that.addClass('more-replies');
                    that.html(commentClosed);
                    that.attr('data-repl',that.text().match(/\d+/g));
                    that.attr('data-page',1);
                    that.html(that.text().replace(/\d+/g,parseInt(that.text().match(/\d+/g))-6))
                }else
                    that.html(commentsOpened);

                if (replying)
                    that.parent().find('.comment-replies-box').show();
                else
                    that.parent().find('.comment-replies-box').hide().show(200);

            },
            error: function () {
                console.log('error - pasuxebi am komentarze ar arsebobs');
            },
            complete: function () {
                if (that.parent().find('.comment-form').length) {
                    window.scroll({
                        top: that.parent().find('.comment-form textarea').offset().top - screen.height / 2 + 50,
                        left: 0,
                        behavior: 'smooth'
                    });
                }
            }
        })
    } else {
        if (that.hasClass('opened')) {
            that.html(commentClosed);
            that.parent().find('.comment-replies-box').hide(200);
        } else {
            that.html(commentsOpened);
            that.parent().find('.comment-replies-box').show(200);
        }
        that.toggleClass('opened closed')
    }
}

$('form').submit(function () {
    let that = $(this);

    that.find('input[type=submit]').each(function () {
        let submitButton = $(this);

        if(submitButton.attr('disabled'))
            return;

        setTimeout(function () {
            submitButton.attr('disabled',true);
            setTimeout(function () {
                submitButton.removeAttr('disabled')
            },3000)
        },0)
    })
});

$('#login-focus').on('click', function () {
    $('.login-form').toggleClass('show');
});

$(".show-ordering").on('click',function () {
    $(".item-page-ordering").toggle();
});

$('.episode-select-button').on('click', function () {
    let clickedButton = $(this);
    let oneVideoURL = clickedButton.data('one');
    let twoVideoURL = clickedButton.data('two');

    let itemPlayer = $('.item-player');
    let choiceEl = $('#players-choice');
    let activatedButton = $('.episode-select-button.active');

    choiceEl.val("myvideo");

    if (oneVideoURL)
        $('.item-player iframe').attr('src', oneVideoURL);
    else
        $('.item-player iframe').attr('src', twoVideoURL);


    if (oneVideoURL && twoVideoURL) choiceEl.removeClass("hidden");
    else choiceEl.addClass("hidden");


    if (clickedButton !== activatedButton) {
        activatedButton.removeClass('active');
        clickedButton.addClass('active');
    }

    if (itemPlayer.hasClass('hidden')) {
        itemPlayer.removeClass('hidden');
    }
    setCookie(itemSlug.substring(7, itemSlug.length - 1), clickedButton.data('id'), 30);
});

$("#players-choice").on("change",function (e) {
    let chosenVideo = $('.episode-select-button.active');
    let value = e.target.value;

    if(value === "myvideo") $('.item-player iframe').attr('src', chosenVideo.data('one'));
    else $('.item-player iframe').attr('src', chosenVideo.data('two'));
});

$('.comment-form').submit(function (e) {
    e.preventDefault();
    let that = $(this);
    let $formDataSerialized = $(this).serialize();
    let text = that.find('textarea').val();
    let validation = validateComment(text);

    if (validation == null) {
        $.ajax({
            method: "POST",
            url: '/account/comment/',
            data: $formDataSerialized + '&id=' + $('.item-page').data('id'),
            success: function (data) {
                data.body = $(".comment-form textarea").val();
                let commentBox = $(".comments-box");

                commentBox.prepend(makeCommentBoxHTML(data));
                readMoreComment(commentBox.find(".comment:first").find('.comment-text'));

                $(".comments-box > .comment:first").hide(10).show(100);
                that.trigger('reset');
            },
            error: function (data) {
                if (data.responseJSON.body.length && data.responseJSON.body[0].code === 'required')
                    alert("კომენტარი ვერ იქნება ცარიელი.");
                else if (data.status === 500)
                    alert("მოხდა ტექნიკური შეცდომა, გთხოვთ მიწეროთ ადმინისტრაციას.");
            },
            complete: function () {
                that.find('button').removeAttr('disabled');
            }
        })
    } else {
        if (text.match(/\[spoiler\](.*?)\[\/spoiler\]/ig) == null)
            that.find('.spoiler-button').removeAttr('disabled');
        alert(validation);
    }
});

$('.comments-box, .comment-form').on('click', '.reply-button', function () {
    let button = $(this);
    let is_replying_parent = true;
    let parent_id = button.data('id');
    let username = button.data('username');
    let lastComment = button.parents('.comment:last');
    let replying_to_id;
    let formHTML;

    if (typeof button.data('it') !== "undefined") {
        is_replying_parent = false;
    }

    if (is_replying_parent) {
        formHTML = makeCommentTextAreaHTML(parent_id);
    } else {
        parent_id = button.data('it');
        replying_to_id = button.data('id');
        formHTML = makeCommentTextAreaHTML(parent_id, replying_to_id);
    }

    button.parent().find('#edit-comment').hide();

    if (lastComment.find('.comment-form').length === 0) {
        lastComment.append(formHTML);
    } else {
        lastComment.find('.comment-form').replaceWith(formHTML);
    }

    let commentForm = lastComment.find('.comment-form');
    commentForm.find('textarea').val(username + ', ').focus();
    let checkRepliesButton = lastComment.find('.comment-replies-check');
    if (checkRepliesButton.length === 1) {
        if (checkRepliesButton.hasClass('closed'))
            getChildComments(checkRepliesButton, parent_id, true);
    }
}).on('click', '.comment-replies-check:not(.more-replies)', function () {
    let that = $(this);
    getChildComments(that, that.data('id'));
}).on("click", ".comment .comment-form button[type=reset]", function (e) {
    e.preventDefault();
    if (confirm('ნამდვილად გსურთ გაუქმება?')) {
        let parent = $(this).parent();
        parent.prev().find('#edit-comment').show();
        parent.remove();
    }
}).on("submit", ".comment .comment-form", function (e) {
    e.preventDefault();
    let that = $(this);
    let $formDataSerialized = that.serialize();
    let validation = validateComment($(this).find('textarea').val());

    that.off('submit');

    if (validation == null) {
        if (typeof that.data('it') !== "undefined") {
            $formDataSerialized += `&parent_id=${that.data('id')}` + `&replying_to_id=${that.data('it')}`;
        } else {
            $formDataSerialized += `&parent_id=${that.data('id')}`;
        }

        $.ajax({
            method: "POST",
            url: '/account/reply_comment/',
            data: $formDataSerialized,
            success: function (data) {
                data.body = that.find('textarea').val();
                let html = '';
                if (that.parent().has('.comment-replies-box').length) {
                    html = makeReplyCommentBoxHTML(data);
                    that.parent().children('.comment-replies-box').append(html)
                } else {
                    that.parent().find('#edit-comment').remove();
                    html += `<div class="comment-replies-check closed" data-id="${that.data('id')}">
                                პასუხების ჩვენება
                             </div>
                             <div class="comment-replies-box"></div>`;
                    that.parent().append(html);
                }
                let replies_box = that.parent().find('.comment-replies-check');

                if (that.parent().find('.comment-replies-check').hasClass('closed'))
                    getChildComments(replies_box, that.data('id'));

                that.remove();
            },
            error: function () {
                that.remove();
            },
        })
    } else
        alert(validation)
}).on('click', '.comment #remove-comment', function () {
    if (confirm('დარწმუნებული ხართ, რომ კომენტარის წაშლა გინდათ? ამ ქმედების შემდეგ კომენტარს ვეღარ აღადგენთ.')) {
        let that = $(this);
        let parent = that.closest('.comment');

        $.ajax({
            method: "DELETE",
            url: '/account/comment/delete/' + parent.find('.comment-info').data('id'),
            success: function (data) {
                parent.fadeOut(200, function () {
                    parent.replaceWith(makeDeletedCommentBoxHTML(data));
                });
            },
            error: function () {
                alert("მოხდა შეცდომა, თავიდან სცადეთ!");
            },
        })
    }
}).on('click', '.comment #edit-comment', function () {
    let that = $(this);
    let commentBox = that.closest('.comment');
    let id = commentBox.find('.comment-info').data('id');
    let commentText = commentBox.find('.comment-text');
    let hasSpoiler = commentText.find('.spoiler').length > 0;
    let textareaValue = HTMLToBB(commentText.html());

    that.toggleClass('hidden');
    commentBox.find('.reply-button,#like-comment,#remove-comment,#dislike-comment,.comment-text').toggleClass('hidden');

    commentBox.append(makeEditTextarea(id, hasSpoiler));
    commentBox.find('.comment-edit-form textarea').focus().val(textareaValue.trim());
}).on('click', '.comment .comment-edit-form button[type=reset]', function (e) {
    e.preventDefault();
    if (confirm('ნამდვილად გსურთ გაუქმება?')) {
        let parent = $(this).parent();
        parent.parent().find('.reply-button,#like-comment,#edit-comment,#remove-comment,#dislike-comment,.comment-text').toggleClass('hidden');
        parent.remove();
    }
}).on('click', '.comment .comment-edit-form button[type=submit]', function (e) {
    e.preventDefault();
    let parent = $(this).parent();
    let finText = parent.find('textarea').val();
    let validation = validateComment(finText);

    if (validation == null) {
        if (HTMLToBB(parent.prev().find('.comment-text')[0].innerHTML) !== finText) {
            let $formSerialized = parent.serialize();
            $.ajax({
                method: "POST",
                url: '/account/comment/edit/',
                data: $formSerialized + '&id=' + parent.data('id'),
                success: function (data) {
                    parent.parent().find('.comment-text').html(makeCommentTextHTML(finText));
                    parent.parent().find('.comment-time').text(convertTimeGeo(data.time));
                    parent.parent().find('.reply-button,#like-comment,#edit-comment,#remove-comment,#dislike-comment,.comment-text').toggleClass('hidden');
                    parent.remove();
                },
                error: function () {
                    parent.parent().find('.reply-button,#like-comment,#edit-comment,#remove-comment,#dislike-comment,.comment-text').toggleClass('hidden');
                    parent.remove();
                },
            })
        } else
            alert('შეცვლა არ მოხდა, რადგან ტექსტი არ შეცვლილა!')
    } else {
        alert(validation);
    }
}).on('click', '#like-comment', function () {
    let that = $(this);
    let parent = $(this).parents('.comment-body');


    if (!parent.find('.comment-user').hasClass('mine')) {
        let id = parent.find('.comment-info').data('id');

        $.ajax({
            method: "POST",
            url: '/account/comment/like/',
            data: {
                id: id
            },
            success: function (data) {
                if (data.type === 1) {
                    that.hide(100, function () {
                        $(this).html(`<i class="fas fa-thumbs-up" aria-hidden="true"></i>` + (parseInt(that.text()) + 1)).show(200);
                    })
                } else if (data.type === 0)
                    that.hide(100, function () {
                        $(this).html(`<i class="far fa-thumbs-up" aria-hidden="true"></i>` + (parseInt(that.text()) - 1)).show(200);
                    });
                else if (data.type === 2) {
                    parent.find('#dislike-comment').hide(100, function () {
                        $(this).html(`<i class="far fa-thumbs-down" aria-hidden="true"></i>` + (parseInt(that.parent().find('#dislike-comment').text()) - 1)).show(200);
                    });
                    that.hide(100, function () {
                        $(this).html(`<i class="fas fa-thumbs-up" aria-hidden="true"></i>` + (parseInt(that.text()) + 1)).show(200);
                    })
                }
            },
            error: function () {
                alert("ლაიქისთვის საჭიროა ავტორიზაცია!");
            },
        })
    } else
        alert('საკუთარი კომენტარის მოწონება/არ მოწონება არ შეიძლება.')
}).on('click', '#dislike-comment', function () {
    let that = $(this);
    let parent = $(this).parents('.comment-body');

    if (!parent.find('.comment-user').hasClass('mine')) {

        let id = parent.find('.comment-info').data('id');
        $.ajax({
            method: "POST",
            url: '/account/comment/dislike/',
            data: {id: id},
            success: function (data) {
                if (data.type === 1)
                    that.hide(100, function () {
                        $(this).html(`<i class="fas fa-thumbs-down" aria-hidden="true"></i>` + (parseInt(that.text()) + 1)).show(200);
                    });
                else if (data.type === 0)
                    that.hide(100, function () {
                        $(this).html(`<i class="far fa-thumbs-down" aria-hidden="true"></i>` + (parseInt(that.text()) - 1)).show(200);
                    });
                else if (data.type === 2) {
                    parent.find('#like-comment').hide(100, function () {
                        $(this).html(`<i class="far fa-thumbs-up" aria-hidden="true"></i>` + (parseInt(that.parent().find('#like-comment').text()) - 1)).show(200);
                    });
                    that.hide(100, function () {
                        $(this).html(`<i class="fas fa-thumbs-down" aria-hidden="true"></i>` + (parseInt(that.text()) + 1)).show(200);
                    })
                }
            },
            error: function () {
                alert("დისლაიქისთვის საჭიროა ავტორიზაცია!");
            },
        })
    } else
        alert('საკუთარი კომენტარის მოწონება/არ მოწონება არ შეიძლება.')
}).on('click', '.spoiler-button', function (e) {
    e.preventDefault();
    let tx = $(this).parent().find('textarea')[0];
    let start = tx.selectionStart;
    let end = tx.selectionEnd;
    let sel = tx.value.substring(start, end);
    tx.value = tx.value.substring(0, start) + '[spoiler]' + sel + '[/spoiler]' + tx.value.substring(end);
    tx.focus();
    tx.selectionEnd = end + 9;
    $(this).attr('disabled', true);
}).on('click', '#reveal-spoiler', function (e) {
    e.stopPropagation();
    $(this).prev().fadeIn();
    $(this).hide();
}).on('click', '.spoiler', function (e) {
    e.stopPropagation();
    $(this).next().fadeIn();
    $(this).hide();
}).on('keyup', 'textarea', function () {
    if (!$(this).val().length)
        $(this).parent().next().removeAttr('disabled');
}).on('click', '.read-more', function (e) {
    e.stopPropagation();
    let that = $(this);
    that.prev().toggle();
    if (that.prev().is(':hidden')) {
        that.prev().toggleClass('hide-this');
        that.prev().slideDown(0);
    } else {
        that.prev().toggleClass('hide-this');
    }
    that.text(function (i, text) {
        return text === "სრულად" ? "დამალვა" : "სრულად";
    });
}).on('click', '.more-replies', function (e) {
    let that = $(this);
    let currentPage = parseInt(that.attr('data-page'));

    $.ajax({
        method: "GET",
        url: '/account/check_replies/' + that.attr('data-id'),
        data: {
            'skip': currentPage + 1,
        },
        success: function (e) {
            let commentRepliesBox = that.next('.comment-replies-box');
            let data = e['replies'];

            for (let i = 0; i < data.length; i++) {
                if (typeof data[i].deleted === "undefined") {
                    commentRepliesBox.prepend(makeReplyCommentBoxHTML(data[i]));
                    readMoreComment(commentRepliesBox.find('.comment:first').find('.comment-text'));
                } else
                    commentRepliesBox.prepend(makeDeletedCommentBoxHTML(data[i]));
            }

            if (e['availablePages'] > currentPage + 1) {
                that.attr('data-page', currentPage + 1);
                that.html(that.text().replace(/\d+/g,parseInt(that.text().match(/\d+/g))-6))
            } else {
                that.removeClass('more-replies');
                that.html(that.text().replace('ჩვენება', 'დამალვა'));
                that.html(that.text().replace(/\d+/g,that.data('repl')))
            }

            commentRepliesBox.hide().fadeIn(50);

        },
        error: function () {
            console.log('error - meti pasuxi am komentarze ar arsebobs');
        },
    })
});

$('.showmore').on('click', function () {
    let that = $(this);
    let current_page = parseInt(that.attr('data-page'));

    let requestParams = {
        method: "GET",
        url: '/account/more_comments/' + $('.item-page').data('id') + "/" + (current_page + 1) + "/"
    };

    if (urlForQueryParams.has("parent")) {
        requestParams.data = {
            parent: urlForQueryParams.get("parent"),
        }
    }

    $.ajax({
        ...requestParams,
        success: function (data) {
            let html = '';
            let commentBox = $(".comments-box");

            for (let i = 0; i < data.length; i++) {
                if (typeof data[i].deleted === "undefined") // not deleted
                    html += makeCommentBoxHTML(data[i]);
                else
                    html += makeDeletedCommentBoxHTML(data[i]);
            }

            commentBox.append(html);
            commentBox.find(`.comment:nth-child(n+${6 * current_page + 1})`).each(function (i, com) {
                readMoreComment($(com).find(('.comment-text')))
            });

            that.attr('data-page', current_page + 1);
            if ((current_page + 1).toString() === that.attr('data-max'))
                that.remove();
        },
        error: function () {
            that.text('მეტი აღარ არის!');
            that.attr('class', 'nomore');
            that.unbind('click');
        },
    })
});

$('.profile-edit button[type=submit]').on('click', function (e) {
    e.preventDefault();
    let selectedDay = parseInt($("select[name='birth-day'] option:selected").val());
    let selectedMon = parseInt($("select[name='birth-month'] option:selected").val());
    let selectedYea = parseInt($("select[name='birth-year'] option:selected").val());
    if (selectedDay !== 0 && selectedMon !== 0 && selectedYea !== 0)
        $('input[name=birth]').val(selectedYea + '-' + selectedMon + '-' + selectedDay);
    else
        $('input[name=birth]').val(null);

    $('#profile-details-form').submit();
});


$('.profile-details-input').on('click', '#change-username-button', function (e) {
    e.preventDefault();
    let that = $(this);
    let inputEl = that.parent().find('input');
    let username = inputEl.val();
    inputEl.attr('readonly', null);
    inputEl.css('background-color', '#FFF');
    inputEl.focus().val('').val(username);
    that.text('დადასტურება');
    that.before(`<button type="reset" class="cancel">გაუქმება</button>`);
    that.attr('id', 'submit-username-button');
}).on('click', '.cancel', function (e) {
    e.preventDefault();
    let that = $(this);
    let parent = that.parent();
    let inputEl = parent.find('input');
    let submitButton = parent.find('#submit-username-button');
    inputEl.attr('readonly', '');
    inputEl.css('background-color', '#aaaa');
    inputEl.val($('#profile-username').text());
    submitButton.text('შეცვლა');
    submitButton.attr('id', 'change-username-button');
    that.remove();
}).on('click', '#change-email-button', function (e) {
    e.preventDefault();
    $.ajax({
        method: "GET",
        url: '/account/email_change/',
        success: function () {
            alert('მოთხოვნა გაიგზავნა თქვენს Email-ზე,გთხოვთ გადაამოწმოთ! შეამოწმეთ Spam ფაილიც!')
        },
        error: function () {
            alert('მოხდა შეცდომა! თავიდან სცადეთ!');
        }
    });
});

$('.notification-page').on('click', '#delete-all', function (e) {
    e.preventDefault();
    let that = $(this);

    $.ajax({
        method: "DELETE",
        url: '/account/notifications/delete/all/' + that.data('content'),
        success: function () {
            let navNotifCountElement = $('.notif-count');
            let navNotifCount = navNotifCountElement.text();
            let notificationsBox = $('.notifications');

            if (navNotifCount > 0) {
                notificationsBox.find('li').each((index, item) => {
                    if (!$(item).hasClass('visited')) {
                        navNotifCount -= 1;
                    }
                });
                navNotifCountElement.text(navNotifCount)
            }

            notificationsBox.html(`<div class="form-title">თქვენ გაქვთ 0 შეტყობინება</div>`);

            $('a.notif-model.active').find('.count').text('(0)');
            that.hide(200).remove();
        },
        error: function () {
            alert('მოხდა შეცდომა! თავიდან სცადეთ!');
        }
    });
}).on('click', '.remove-notif', function (e) {
    let that = $(this);

    e.preventDefault();
    $.ajax({
        method: "DELETE",
        url: '/account/notifications/delete/' + that.data('id'),
        success: function () {
            let newNotifCountElement = $('a.notif-model.active').find('.count');
            let newNotifCount = newNotifCountElement.text().match(/\d+/g);

            let notificationsBox = $('.notifications');
            let allNotifCount = notificationsBox.find('li').length;

            if (allNotifCount - 1 === 0) {
                $('#delete-all').hide(200).remove();
                notificationsBox.html(`<div class="form-title">თქვენ გაქვთ 0 შეტყობინება</div>`);
            }

            if (!that.parent().hasClass('visited')) {
                let notifCount = $('.notif-count');
                notifCount.text(notifCount.text() - 1);
                newNotifCountElement.text(`(${newNotifCount[0] - 1})`)
            }

            that.parents('li').hide(200).remove();
        },
        error: function () {
            alert('მოხდა შეცდომა! თავიდან სცადეთ!');
        }
    });
}).on('click', '.nav-icon', function () {
    $('.notif-model').toggleClass('show hide')
});
