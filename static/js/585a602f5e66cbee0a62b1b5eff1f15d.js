/*
* Animilia.ge - Staff tools script
* Author: Morpheus
* jQuery v3.4.1
* */

"use strict";

const userId = window.location.pathname.split('/')[2];
const hasAvatar = $('#active-avatar').attr('src') !== '/media/no-avatar.jpg?r=1';

$(function () {
    const profileBox = $(".profile-display");

    profileBox.find('#profile-username').after(profilePreviewUsetSettingsIcon);
    profileBox.append(userSettingsModal);
});

// Markups
const profilePreviewUsetSettingsIcon = `<span class='user-settings-icon' id='user-settings'><i class=\"fas fa-user-cog\"></i></span>`;
const userSettingsModal =
    `<div id="settings-modal">
      <div class="modal-content">
        <span class="close">&times;</span>
        
        <div class="modal-body">
            <button id="delete-avatar" class="upload-result" ${!hasAvatar ? `disabled` : ``} onclick="deleteAvatar(this)">ავატარის წაშლა</button>
            <button id="show-info" class="upload-result" onclick="showInfo(this)">ინფოს ნახვა</button>
            <button id="send-message" class="upload-result" onclick="showMessageForm()">შეტყობინების გაგზავნა</button>
            <hr>
            <div id="action-content" style="margin-top: 12px"></div>
        </div>
      </div>
    </div>`;
const messageForm =
    `<form method="post" id="message-form">
        <div class="form-group">
            <input type="text" name="subject" class="form-input" placeholder="სათაური" maxlength="50" required id="id_subject">
        </div>
        <div class="form-group">
            <textarea name="body" cols="40" rows="10" placeholder="წერილი" class="form-input" required="" id="id_body"></textarea>
       </div>
        <input type="submit" id="submit" class="form-submit" value="გაგზვნა">
      </form>`;

function deleteAvatar(e) {
    if (confirm('ნამდვილად გინდა წაშლა?')) {
        $.ajax({
            url: "/staff/avatar_delete/" + userId,
            type: "DELETE",
            success: function () {
                $('#active-avatar').attr('src', '/media/no-avatar.jpg');
                e.disabled = true;
            },
            error: function () {
                alert('მოხდა შეცდომა!')
            }
        });
    }
}

function showInfo(e) {
    $.ajax({
        url: "/staff/show_info/" + userId,
        type: "GET",
        success: function (data) {
            $('#action-content').html(makeUserInfoTable(data));
            e.disabled = true;
        },
        error: function () {
            alert('მოხდა შეცდომა!')
        }
    });
}

function makeUserInfoTable(data) {
    let html = '<table style="width: 100%">';

    Object.keys(data).forEach((item) => {
        html += `<tr><td>${item}</td><td>${data[item]}</td></tr>`
    });

    html += '</table>';

    return html
}

function showMessageForm(){
    $('#action-content').html(messageForm);
}

$(window).click(function (e) {
    if (e.target.id === 'settings-modal') {
        $('#settings-modal').css('display', 'none')
    }
});


$(".profile-display").on('click', '#user-settings', function () {
    $('#settings-modal').toggle();
}).on('click', '.close', function () {
    $('#settings-modal').css('display', 'none')
}).on('submit','#message-form',function (e) {
    e.preventDefault();
    let that = $(this);

    if (confirm('ნამდვილად გინდა გაგზავნა?')) {
        $.ajax({
            url: "/staff/send_message/" + userId,
            type: "POST",
            data: that.serialize(),
            success: function () {
                that.trigger('reset');
            },
            error: function () {
                alert('მოხდა შეცდომა!');
            },
        });
    }
});