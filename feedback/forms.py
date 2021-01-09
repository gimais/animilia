from django import forms

from .models import Feedback, Message


class FeedbackForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'user_username' in kwargs:
            self.user_username = kwargs.pop('user_username')
            self.user_email = kwargs.pop('user_email')
        else:
            self.user_username = ''
            self.user_email = ''
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields['customer_name'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'სახელი',
            'value': self.user_username,
        })
        self.fields['email'].widget = forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email (გთხოვთ მიუთითეთ ის Email, რომელზეც გინდათ მიიღოთ პასუხი)',
            'value': self.user_email,
        })

    customer_name = forms.CharField(max_length=50)

    email = forms.EmailField(max_length=254)

    details = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'წერილი', 'class': 'form-input', })
    )

    class Meta:
        model = Feedback
        fields = ('customer_name', 'email', 'details',)


def FeedbackReplyForm(obj):
    class Form(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            kwargs['initial'].update({'to_user': obj.registered_user, 'subject': 'კონტაქტი #{}'.format(obj.id)})
            super(Form, self).__init__(*args, **kwargs)

            self.fields['to_user'].widget.attrs['disabled'] = True

        class Meta:
            model = Message
            fields = ('to_user', 'subject', 'body')

    return Form
