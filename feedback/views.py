from django.contrib import messages
from django.shortcuts import render
from .forms import FeedbackForm

# Create your views here.

def feedback_form(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

            if x_forwarded_for:
                ipaddress = x_forwarded_for.split(',')[-1].strip()
            else:
                ipaddress = request.META.get('REMOTE_ADDR')

            form.ip = ipaddress

            if request.user.is_authenticated:
                form.registered_user = request.user

            form.save()
            messages.success(request, 'თქვენი წერილი წარმატებით გაიგზავნა.', extra_tags='welcome')
            return render(request,'feedback.html',{'form':FeedbackForm()})
    else:
        if request.user.is_authenticated:
            form = FeedbackForm(user_username=request.user.get_username(),user_email=request.user.email)
        else:
            form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form})
