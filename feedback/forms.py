from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'სახელი'}))

    email = forms.EmailField(max_length=254, widget=forms.EmailInput(
        attrs={'class': 'form-input', 'placeholder': 'Email'}))

    details = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={'placeholder': 'წერილი','class': 'form-input',})
    )

    class Meta:
        model = Feedback
        fields = ('customer_name','email','details',)