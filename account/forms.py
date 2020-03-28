from django import forms
from django.contrib.auth.password_validation import MinimumLengthValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, \
    PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.utils.translation import ngettext
from django.utils import timezone
from account.models import Comment, Profile
from account.validators import SignUpMaxLengthValidator


def validate(self, password, user=None):
    if len(password) < self.min_length:
        raise forms.ValidationError(
            ngettext(
                "ეს პაროლი მოკლეა. ის უნდა შეიცავდეს მინიმუმ %(min_length)d სიმბოლოს.",
                "ეს პაროლი მოკლეა. ის უნდა შეიცავდეს მინიმუმ %(min_length)d სიმბოლოს.",
                self.min_length
            ),
            code='password_too_short',
            params={'min_length': self.min_length},
        )

MinimumLengthValidator.validate = lambda self,password,user:validate(self,password,user)


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
        label='',
        widget=forms.PasswordInput(attrs={'class':'form-input','placeholder':'გაიმეორეთ პაროლი'}),
        strip=False,
        help_text="",
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
    error_messages = {
        'password_mismatch': ('მოცემული პაროლები არ ემთხვევა.'),
        'password_incorrect': ("ძველი პაროლი არასწორია. გთხოვთ,თავიდან სცადოთ."),
    }

    old_password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password','class': 'form-input',
                                          'placeholder':'ძველი პაროლი'}),
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


class UpdateUsernameForm(forms.ModelForm):

    error_messages = {
        'not_changed': "თქვენ ეს ნიკი ისედაც გაქვთ!",
        'deadline':'ნიკის შეცვლა შეგიძლიათ ყოველ 7 დღეში ერთხელ!'
    }
    class Meta:
        model = User
        fields = ('username',)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UpdateUsernameForm, self).__init__(*args, **kwargs)


    def clean_username(self):
        old_username = self.user.username
        username = self.cleaned_data.get('username')

        if username == old_username:
            raise forms.ValidationError(
                self.error_messages['not_changed'],
                code='not_changed',
            )

        updated_time_difference = (timezone.now() - self.user.settings.username_updated).total_seconds()
        if updated_time_difference < 604800:
            raise forms.ValidationError(
                self.error_messages['deadline'],
                code='deadline',
            )

        return username

    def save(self, commit=True):
        username = self.cleaned_data["username"]
        self.user.username = username
        self.user.settings.username_updated = timezone.now()

        if commit:
            self.user.save()

        return self.user

class UpdateProfileForm(forms.ModelForm):
    gender = forms.Select()
    birth = None

    class Meta:
        model = Profile
        fields = ('gender', 'birth')

class EmailChangeForm(forms.Form):
    """
    A form that lets a user change set their email while checking for a change in the
    e-mail.
    """
    error_messages = {
        'email_mismatch': "მოცემული Email-ები არ ემთხვევა ერთმანეთს!",
        'not_changed': "ეს Email ისედაც გაქვთ!",
    }

    new_email1 = forms.EmailField(max_length=254,widget=forms.EmailInput(
        attrs={'class':'form-input','placeholder':'ახალი Email'}))

    new_email2 = forms.EmailField(max_length=254,widget=forms.EmailInput(
        attrs={'class':'form-input','placeholder':'გაიმეორეთ ახალი Email'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_new_email1(self):
        old_email = self.user.email
        new_email1 = self.cleaned_data.get('new_email1')
        if new_email1 and old_email:
            if new_email1 == old_email:
                raise forms.ValidationError(
                    self.error_messages['not_changed'],
                    code='not_changed',
                )
        return new_email1

    def clean_new_email2(self):
        new_email1 = self.cleaned_data.get('new_email1')
        new_email2 = self.cleaned_data.get('new_email2')
        if new_email1 and new_email2:
            if new_email1 != new_email2:
                raise forms.ValidationError(
                    self.error_messages['email_mismatch'],
                    code='email_mismatch',
                )
        return new_email2

    def save(self, commit=True):
        email = self.cleaned_data["new_email1"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user