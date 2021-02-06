from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from .forms import FeedbackForm, AuthFeedbackForm
from .models import Message

# Create your views here.


def feedback(request):
    form_class = AuthFeedbackForm if request.user.is_authenticated else FeedbackForm

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[-1].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            form.ip = ip_address

            if form_class == AuthFeedbackForm:
                form.customer_name = request.user.username
                form.email = request.user.email
                form.registered_user = request.user

            form.save()
            messages.success(request, 'თქვენი წერილი წარმატებით გაიგზავნა.', extra_tags='welcome')
            return render(request, 'feedback.html', {'form': form_class()})
        return render(request, 'feedback.html', {'form': form})
    return render(request, 'feedback.html', {'form': form_class()})


def get_message(request, id):
    message = get_object_or_404(Message.objects.filter(to_user=request.user), id=id)

    if request.GET.get('visited', None) == '0':
        message.notification.filter(seen=False).update(seen=True)

    return JsonResponse({
        'message': message.body
    }, status=200)
