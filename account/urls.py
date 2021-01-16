from django.urls import path
from . import views as local_view
from django.contrib.auth import views
from .decorators import anonymous_required
from .forms import MyAuthenticationForm,MyPasswordResetForm,MyPasswordChangeForm,MySetPasswordForm

# Forms
views.LoginView.authentication_form = MyAuthenticationForm

views.PasswordResetView.form_class = MyPasswordResetForm

views.PasswordChangeView.form_class = MyPasswordChangeForm
views.PasswordChangeView.success_url = '/account/profile'

views.PasswordResetConfirmView.form_class = MySetPasswordForm


urlpatterns = [
    path('register/',local_view.signup_view,name='signup'),
    path('login/', local_view.login_view, name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('notifications/',local_view.check_notification,name='notification'),
    path('notifications/delete/<int:id>',local_view.delete_notification,name='notification'),

    path('profile/',local_view.profile_view,name='profile'),
    path('avatar_update/',local_view.avatar_update,name='avatar_update'),
    path('avatar_update/delete/', local_view.avatar_delete, name='avatar_delete'),
    path('username_update/',local_view.username_update,name='username_update'),

    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),

    path('email_change/<uidb64>/<token>/',local_view.change_email_view, name='change_email'),
    path('email_change/',local_view.change_email_request_view, name='change_email_request'),

    path('password_reset/', anonymous_required(views.PasswordResetView.as_view()), name='password_reset'),
    path('password_reset/done/',anonymous_required(views.PasswordResetDoneView.as_view()), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('comment/', local_view.add_comment, name='comment'),
    path('reply_comment/', local_view.reply_comment, name='reply_comment'),
    path('check_replies/<int:id>', local_view.check_replies, name='replies_check'),

    path('comment/delete/<int:id>', local_view.delete_comment, name='comment_delete'),
    path('comment/edit/', local_view.edit_comment, name='comment_edit'),
    path('comment/like/', local_view.like_comment, name='comment_like'),
    path('comment/dislike/', local_view.dislike_comment, name='comment_dislike'),
]