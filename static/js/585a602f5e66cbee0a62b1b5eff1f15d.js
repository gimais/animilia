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
<!--            <button id="delete-avatar" class="upload-result">შეტყობინების გაგზავნა</button>-->
            <div id="action-content" style="margin-top: 12px"></div>
        </div>
      </div>
    </div>`;

$(window).click(function (e) {
    if (e.target.id === 'settings-modal') {
        $('#settings-modal').css('display', 'none')
    }
});


$(".profile-display").on('click', '#user-settings', function () {
    $('#settings-modal').toggle();
}).on('click', '.close', function () {
    $('#settings-modal').css('display', 'none')
});


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