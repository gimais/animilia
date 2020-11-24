from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, \
    PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
from django.utils.safestring import mark_safe

from account.models import Comment, Profile, Settings
from account.validators import MyUnicodeUsernameValidator,blacklist,ERRORS

User._meta.get_field('username').validators[0] = MyUnicodeUsernameValidator()
User._meta.get_field('username').validators[1] = MaxLengthValidator(16)
User._meta.get_field('username').validators.append(MinLengthValidator(3))

class SignUpForm(UserCreationForm):
    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop("autofocus", None)

    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Email'}))

    password1 = forms.CharField(
        label="",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'პაროლი (მინ 4 სიმბოლო)'}),
        help_text='',
    )
    password2 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'გაიმეორეთ პაროლი'}),
        strip=False,
        help_text="",
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username.lower() in blacklist:
            raise forms.ValidationError(
                ERRORS['blacklist'],
                code='blacklist'
            )

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                ERRORS['unique'],
                code='unique'
            )

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                mark_safe(ERRORS['unique_email']),
                code='unique_email'
            )
        return email

    class Meta:
        model = User

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ნიკი (მინ: 3 - მაქს: 16)'})
        }

        fields = ('username', 'email', 'password1', 'password2',)


class MyAuthenticationForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    raise self.get_invalid_login_error()
            else:
                try:
                    user = User.objects.get(username__iexact=username)
                except User.DoesNotExist:
                    raise self.get_invalid_login_error()

            if user.check_password(password):
                self.confirm_login_allowed(user)

            self.user_cache = authenticate(self.request, username=user, password=password)

            if self.user_cache is None:
                raise self.get_invalid_login_error()
        else:
            raise forms.ValidationError(
                ERRORS['empty_fields'],
                code='empty_fields'
            )

        return self.cleaned_data


class MyPasswordResetForm(PasswordResetForm):
    use_required_attribute = False

    email = forms.EmailField(
        label='',
        max_length=254,
        widget=forms.TextInput(attrs={'autocomplete': 'email', 'class': 'form-input', 'placeholder': 'Email'})
    )

#check
class MySetPasswordForm(SetPasswordForm):
    use_required_attribute = False

    new_password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-input', 'placeholder': 'ახალი პაროლი'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-input', 'placeholder': 'გაიმეორეთ ახალი პაროლი'}),
    )


class MyPasswordChangeForm(PasswordChangeForm):
    use_required_attribute = False

    old_password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-input',
                                          'placeholder': 'ძველი პაროლი'}),
    )

    new_password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-input', 'placeholder': 'ახალი პაროლი'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="",
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-input', 'placeholder': 'გაიმეორეთ ახალი პაროლი'}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

class CommentForm(forms.ModelForm):
    body = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={'placeholder': 'კომენტარი'}),
    )

    class Meta:
        model = Comment
        fields = ('body',)

class UpdateUsernameForm(forms.ModelForm):
    error_messages = {
        'not_changed': "ეს ნიკი ისედაც გაქვთ!",
        'deadline': 'ნიკის შეცვლა შეგიძლიათ ყოველ 7 დღეში ერთხელ!',
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

        if username.lower() in blacklist:
            raise forms.ValidationError(
                ERRORS['blacklist'],
                code='blacklist',
            )

        if User.objects.filter(username__iexact=username).exclude(username=old_username).exists():
            raise forms.ValidationError(
                ERRORS['unique'],
                code='unique',
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


class ShowProfileForm(forms.ModelForm):
    show_gender = forms.BooleanField(widget=forms.CheckboxInput(attrs={'style': 'display:inline-block;'}),
                                     required=False)
    show_birth = forms.BooleanField(widget=forms.CheckboxInput(attrs={'style': 'display:inline-block;'}),
                                    required=False)

    class Meta:
        model = Settings
        fields = ('show_gender', 'show_birth',)

class EmailChangeForm(forms.Form):
    use_required_attribute = False

    error_messages = {
        'email_mismatch': "მოცემული Email-ები არ ემთხვევა ერთმანეთს!",
        'not_changed': "ეს Email ისედაც გაქვთ!",
    }

    new_email1 = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'ახალი Email'}))

    new_email2 = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'გაიმეორეთ ახალი Email'}))

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
            if User.objects.filter(email=new_email1).exists():
                raise forms.ValidationError(
                    mark_safe(ERRORS['unique_email']),
                    code='unique_email'
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
