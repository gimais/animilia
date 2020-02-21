from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from account.forms import SignUpForm,MyAuthenticationForm
from animilia.settings import LOGIN_REDIRECT_URL

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = MyAuthenticationForm(data=request.POST)
        if form.is_valid():
            # log the user in
            login(request, form.get_user())
            messages.success(request,'გამარჯობა, {}'.format(form.get_user()),extra_tags='green')
            return HttpResponseRedirect(LOGIN_REDIRECT_URL)
        else:
            messages.error(request, 'ნიკი ან პაროლი არასწორია. თავიდან სცადეთ!',extra_tags='red')
            return HttpResponseRedirect('/')
    else:
        messages.warning(request,'ნუ ჩათლახობ! O_o ',extra_tags='maimuni')
        return HttpResponseRedirect('/')


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