from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, \
    PasswordChangeForm, SetPasswordForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator,MaxLengthValidator

from django.utils import timezone
from account.models import Comment, Profile
from account.validators import SignUpMaxLengthValidator


class SignUpForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop("autofocus", None)


    error_messages = {
        'password_mismatch': 'შეყვანილი პაროლები არ დაემთხვა!',
    }

    email = forms.EmailField(max_length=254,widget=forms.EmailInput(
        attrs={'class':'form-input','placeholder':'Email'}))
    password1 = forms.CharField(
        min_length=4,
        label="",
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-input','placeholder':'პაროლი (მინ 4 სიმბოლო)'}),
        help_text='',
    )
    password2 = forms.CharField(
        min_length=4,
        label='gwgw',
        widget=forms.PasswordInput(attrs={'class':'form-input','placeholder':'გაიმეორეთ პაროლი'}),
        strip=False,
        help_text="შეიყვანეთ იგივე პაროლი.",
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('ეს Email უკვე დარეგისტრირებულია.')
        return email

    class Meta:
        model = User


        User.username_validator.message = "ნიკი შეიძლება შეიცავდეს მხოლოდ ასოებს,ციფრებსა და @/./+/-/_ სიმბოლოებს."
        User._meta.get_field('username').validators[1] = SignUpMaxLengthValidator(16)
        User._meta.get_field('username').validators.append(MinLengthValidator(3))
        MinLengthValidator.message = "სიგრძე მინიმუმ %(limit_value)d სიმბოლოსგან უნდა შედგებოდეს. (შეყვანილია %(show_value)d სიმბოლო)"
        User._meta.get_field('username').error_messages['unique'] = 'ეს ნიკი დაკავებულია!'

        help_texts={
            'username' : '',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input','placeholder':'ნიკი (მინ: 3 - მაქს: 16)'}),
            'autofocus':None,
        }

        fields = ('username', 'email', 'password1', 'password2',)


class MyAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': (
            "გთხოვთ შეიყვანოთ სწორი ნიკი და პაროლი"
        ),
        'inactive': "ეს ანგარიში არააქტიურია!",
    }
    # username = UsernameField(
    #     widget=forms.TextInput(attrs={'class': 'form-input','autofocus': True,'placeholder':'ნიკი'}),
    #     label='',
    # )
    # password = forms.CharField(
    #     label='',
    #     strip=False,
    #     widget=forms.PasswordInput(attrs={'autocomplete': 'current-password','class': 'form-input','placeholder':'პაროლი'}),
    # )

class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='',
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email','class': 'form-input','placeholder':'Email'})
    )

class MySetPasswordForm(SetPasswordForm):
    error_messages = {
        'password_mismatch': ('მოცემული პაროლები არ ემთხვევა.'),
    }
    new_password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','class': 'form-input','placeholder':'ახალი პაროლი'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','class': 'form-input','placeholder':'გაიმეორეთ ახალი პაროლი'}),
    )



class MyPasswordChangeForm(PasswordChangeForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

    error_messages = {
        'password_mismatch': ('მოცემული პაროლები არ ემთხვევა.'),
        'password_incorrect': ("ძველი პაროლი არასწორია. გთხოვთ,თავიდან სცადოთ."),
    }

    old_password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password','required':False,
                                          'class': 'form-input','placeholder':'ძველი პაროლი'}),
    )

    new_password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','class': 'form-input','placeholder':'ახალი პაროლი'}),
        strip=False,
        # help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','class': 'form-input','placeholder':'გაიმეორეთ ახალი პაროლი'}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']


class CommentForm(forms.ModelForm):
    body = forms.CharField(
        label = "",
        widget = forms.Textarea(attrs={'placeholder':'კომენტარი'})
    )

    class Meta:
        model = Comment
        fields = ('body',)





class UpdateUserForm(UserChangeForm):
    username = forms.CharField(required=False)
    email = None
    first_name = None
    last_name = None
    password = None

    class Meta:
        model = User
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance', None)
        super(UpdateUserForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        print(username,self.user)
        if username != self.user.username:
            updated_time_difference = (timezone.now() - self.user.settings.username_updated).total_seconds()
            if updated_time_difference >= 1209600:
                self.user.settings.username_updated = timezone.now()
            else:
                raise ValidationError('ნიკის შეცვლა შეგიძლიათ ყოველ 14 დღეში ერთხელ')

        return username


    # def clean_email(self):
    #     print(self.cleaned_data.get('email'))
    #     username = self.cleaned_data.get('username')
    #     email = self.cleaned_data.get('email')
    #
    #     if email and User.objects.filter(email=email).exclude(username=username).count():
    #         raise forms.ValidationError('ეს EMAIL უკვე გამოყენებულია!')
    #     return email

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     # username = self.cleaned_data.get('username',None)
    #     # user.email = self.cleaned_data['email']
    #
    #     if commit:
    #         user.save()


class UpdateProfileForm(forms.ModelForm):
    # avatar = None
    gender = forms.Select()
    birth = forms.DateField(required=False,widget=forms.DateInput(attrs={'min':'1940-01-01','type':'date'}))


    class Meta:
        model = Profile
        fields = ('gender', 'birth')


# class UpdateAvatarForm(forms.ModelForm):
#
#     class Meta:
#         model = Profile
#         fields = ('avatar',)
#