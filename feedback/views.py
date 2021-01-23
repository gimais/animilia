from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .forms import FeedbackForm, AuthFeedbackForm

# Create your views here.
from .models import Message


def feedback(request):
    if request.method == 'POST':
        form = AuthFeedbackForm(request.POST) if request.user.is_authenticated else FeedbackForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[-1].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            form.ip = ip_address

            if request.user.is_authenticated:
                form.customer_name = request.user.username
                form.email = request.user.email
                form.registered_user = request.user

            form.save()
            messages.success(request, 'თქვენი წერილი წარმატებით გაიგზავნა.', extra_tags='welcome')
            return render(request, 'feedback.html', {'form': FeedbackForm()})
    return render(request, 'feedback.html', {
        'form': AuthFeedbackForm() if request.user.is_authenticated else FeedbackForm()
    })


def get_message(request, id):
    message = get_object_or_404(Message, id=id)

    if message.to_user == request.user:
        message.notification.filter(seen=False, user_id=request.user).update(seen=True)

        return JsonResponse({
            'message': message.body
        }, status=200)

    return JsonResponse({'error': 'araavtorizebuli motxovna'}, status=401)
