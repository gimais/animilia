from django.urls import path
from . import views as local_view
from django.contrib.auth import views
from .forms import MyAuthenticationForm,MyPasswordResetForm,MyPasswordChangeForm

# Forms
views.LoginView.authentication_form = MyAuthenticationForm
views.PasswordResetView.form_class = MyPasswordResetForm
views.PasswordChangeView.form_class = MyPasswordChangeForm

urlpatterns = [
    path('register/',local_view.signup_view,name='signup'),
    path('profile/',local_view.profile_view,name='profile'),

    path('login/', local_view.login_view, name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]