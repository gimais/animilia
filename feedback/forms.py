from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    # customer_name = forms.CharField(
    #     label="",
    #     widget=forms.Textarea(attrs={'placeholder': 'კომენტარი'})
    # )
    #
    # email = forms.EmailField()
    #
    # body = forms.CharField(
    #     label="",
    #     widget=forms.Textarea(attrs={'placeholder': 'კომენტარი'})
    # )

    class Meta:
        model = Feedback
        fields = ('customer_name','email','details',)