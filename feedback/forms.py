from django import forms

from .models import Feedback, Message


class FeedbackForm(forms.ModelForm):

    customer_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'სახელი'}))

    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Email'}))

    body = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'წერილი', 'class': 'form-input', })
    )

    class Meta:
        model = Feedback
        fields = ('customer_name', 'email', 'body',)


class AuthFeedbackForm(forms.ModelForm):

    body = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'წერილი', 'class': 'form-input', })
    )

    class Meta:
        model = Feedback
        fields = ('body',)


def FeedbackReplyForm(obj):
    class Form(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            kwargs['initial'].update({'to_user': obj.registered_user, 'subject': 'კონტაქტი #{}'.format(obj.id)})
            super(Form, self).__init__(*args, **kwargs)

        class Meta:
            model = Message
            fields = ('to_user', 'subject', 'body')

    return Form
