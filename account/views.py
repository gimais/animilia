from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from account.forms import SignUpForm,MyAuthenticationForm

# Create your views here.
def login_view(request):
    next_page = request.GET.get('next') or request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        form = MyAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request,'გამარჯობა, {}'.format(form.get_user()),extra_tags='green')
            return HttpResponseRedirect(next_page)
        else:
            messages.error(request, 'ნიკი ან პაროლი არასწორია. თავიდან სცადეთ!',extra_tags='red')
            return HttpResponseRedirect(next_page)
    else:
        messages.error(request,'მოხდა შეცდომა,თავიდან სცადეთ!',extra_tags='red')
        return HttpResponseRedirect(next_page)

def signup_view(request):
    if request.user.is_anonymous:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('profile')
        else:
            form = SignUpForm()
        return render(request, 'account/signup.html', {'register': form})
    else:
        messages.warning(request,'{}, თქვენ უკვე რეგისტრირებული ხართ!'.format(request.user.username),extra_tags='gray')
        return redirect('home')


def profile_view(request):
    username = request.user.username
    return render(request,'account/profile.html',{'username':username})