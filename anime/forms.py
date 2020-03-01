from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    body = forms.CharField(
        label = "",
        widget = forms.Textarea(attrs={'placeholder':'კომენტარი'})
    )

    class Meta:
        model = Comment
        fields = ('body',)
