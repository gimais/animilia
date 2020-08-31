from django.http import JsonResponse
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
            form.save()
            return JsonResponse({'success': 'true'}, status=200)
    return JsonResponse({'status':'false','info':'moxda shecdoma!'},status=400)
