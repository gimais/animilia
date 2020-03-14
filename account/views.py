import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from PIL import Image
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from .tokens import email_change_token
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.base import View

from account.forms import SignUpForm, MyAuthenticationForm, CommentForm, MyPasswordChangeForm,\
    UpdateProfileForm,UpdateUserForm
from anime.models import Anime
from .models import Comment, Profile

ERROR = {'error':'მოხდა შეცდომა!'}

def login_view(request):
    next_page = request.GET.get('next') or request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        form = MyAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request,'გამარჯობა, {}'.format(form.get_user()),extra_tags='welcome')
            return HttpResponseRedirect(next_page)
        else:
            messages.error(request, 'ნიკი ან პაროლი არასწორია. თავიდან სცადეთ!',extra_tags='failedAuth')
            return HttpResponseRedirect(next_page)
    else:
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
        return redirect('home')

def profile_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            profile_form = UpdateProfileForm(request.POST,request.FILES,instance=request.user.profile)
            user_form = UpdateUserForm(request.POST,instance=request.user)
            u_valid = False
            p_valid = False
            if profile_form.is_valid():
                profile_form.save()
                p_valid = True
            if user_form.is_valid():
                user_form.save()
                u_valid = True
            if p_valid and u_valid:
                return HttpResponseRedirect(reverse('profile'))
        else:
            profile_form = UpdateProfileForm(instance=request.user.profile)
            user_form = UpdateUserForm(instance=request.user)
        context = {
            'p_form':profile_form,
            'u_form':user_form
        }
        return render(request, 'account/profile.html', context)
    else:
        return redirect('home')


def avatar_update(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            is_type = request.POST.get('type',None)
            if is_type is not None:
                profile = request.user.profile
                profile.avatar = 'no-avatar.jpg'
                profile.save()
                return JsonResponse({'success': True,'info':'ავატარი წაიშალა!'}, status=200)
            avatar = request.FILES.get('data',None)
            if avatar:
                check_avatar = Image.open(avatar)
                if check_avatar.format!="JPEG" or check_avatar.size[0] > 200 or check_avatar.size[1] > 200:
                    return JsonResponse({'success':True,'info':'არ აკმაყოფილებს პირობებს!'})

                profile = request.user.profile
                settings = request.user.settings

                # settings update
                settings.avatar_updated = timezone.now()
                settings.save()

                # uploading and saving
                avatar.name = request.user.username + '_{}'.format(settings.avatar_updated.date()) + '.jpg'
                profile.avatar = request.FILES.get('data')
                profile.save()

                return JsonResponse({'success':True,
                                     'time':datetime.datetime.timestamp(settings.avatar_updated+datetime.timedelta(days=3)),
                                     'new_avatar':'avatars/{}'.format(avatar.name),
                                     }, status=200)
            else:
                return JsonResponse({'success': False,'info':'მოხდა შეცდომა!'},status=400)
        else:
            pass
        return render(request, 'account/profile.html')
    else:
        return redirect('home')


# COMMENT SYSTEM

def add_comment(request):
    if request.is_ajax() and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                parent_id = int(request.POST.get('parent_id',False))
                parent_comment = Comment.objects.get(id=parent_id)
            except (TypeError, ValueError, OverflowError,Comment.DoesNotExist):
                parent_comment = None

            if parent_comment:
                anime = Anime.objects.get(id=parent_comment.anime.id)

                reply_comment = form.save(commit=False)
                reply_comment.anime = anime
                reply_comment.parent = parent_comment
                reply_comment.user = request.user
                reply_comment.save()

                response_data = {
                    'username':request.user.username,
                    'avatar':request.user.profile.avatar.name,
                    'user_id':request.user.id, # ar washalooo ? edit da remove functiebistvis rom daadasturos js-shi
                    'comment_id':reply_comment.id,
                }
                status = 200
            else:
                try:
                    anime = Anime.objects.get(id=request.POST['id'])
                except (TypeError, ValueError, OverflowError,Anime.DoesNotExist):
                    anime = None

                if anime:
                    comment = form.save(commit=False)
                    comment.anime = anime
                    comment.user = request.user
                    comment.save()

                    response_data = {
                        'username':request.user.username,
                        'avatar':request.user.profile.avatar.name,
                        'user_id':request.user.id,
                        'comment_id':comment.id
                    }

                    status = 200
                else:
                    response_data = {
                        'error':'ასეთი ანიმე ID მონაცემი ბაზაში არ არის!',
                    }
                    status = 400
            return JsonResponse(response_data,status=status)

        else:
            return JsonResponse(ERROR, status=400)
    else:
        return JsonResponse({'error':"არაავტორიზებული მოთხოვნა!"},status=401)


def check_replies(request,int):
    if request.is_ajax():
        try:
            replies = Comment.objects.filter(parent=int)
        except (Comment.DoesNotExist,Comment.MultipleObjectsReturned):
            replies = None

        if replies:
            result = list()
            for reply in replies:
                result.append(reply.get_reply_comment_info())
            return JsonResponse(result, status=200,safe=False)
        else:
            return JsonResponse({'error':'პასუხები არ არსებობს!'},status=400)
    return JsonResponse(ERROR, status=400)


def delete_comment(request):
    if request.user.is_authenticated:
        try:
            comment_id = Comment.objects.get(id=request.POST.get('id',False))
        except (TypeError, ValueError, OverflowError,Comment.DoesNotExist):
            comment_id = None

        if comment_id:
            if request.user == comment_id.user:
                comment_id.active = False
                comment_id.save()
                response_data = {
                    'info': 'კომენტარი წაიშალა!'
                }
                status = 200
            else:
                response_data = {
                    'error': 'სხვის კომენტარს ვერ წაშლი!'
                }
                status = 401
        else:
            response_data = {
                'error':'ასეთი კომენტარი არ არსებობს!'
            }
            status = 400

        return JsonResponse(response_data,status=status)
    else:
        return JsonResponse({'error':"არაავტორიზებული მოთხოვნა!"},status=401)


def edit_comment(request):
    if request.user.is_authenticated:
        try:
            comment_id = Comment.objects.get(id=request.POST.get('id',False))
        except (TypeError, ValueError, OverflowError,Comment.DoesNotExist):
            comment_id = None

        body = request.POST.get('body',None)

        if comment_id and body:
            if request.user == comment_id.user and comment_id.like.count() == 0 and \
                    comment_id.dislike.count() == 0 and comment_id.replies.count() == 0 and comment_id.active:

                comment_id.body = body
                comment_id.created = timezone.now()
                comment_id.save()

                response_data = {
                    'info': 'კომენტარი შეიცვალა!',
                    'time':datetime.datetime.timestamp(comment_id.created),
                }
                status = 200
            else:
                response_data = {
                    'error': 'მოხდა შეცდომა!'
                }
                status = 401 if request.user.id != comment_id.user.id else 400
        else:
            response_data = {
                'error':'მოხდა შეცდომა!'
            }
            status = 400

        return JsonResponse(response_data,status=status)
    else:
        return JsonResponse({'error':"არაავტორიზებული მოთხოვნა!"},status=401)


def like_comment(request):
    if request.user.is_authenticated:
        try:
            comment_id = Comment.objects.get(id=request.POST.get('id',False))
        except (TypeError, ValueError, OverflowError,Comment.DoesNotExist):
            comment_id = None

        if comment_id and comment_id.user != request.user:

            if comment_id.dislike.filter(id=request.user.id).exists(): # თუ დისლაიქი აქვს კომს წაშალე დისლაქი და დაამატე ლაიქი
                comment_id.dislike.remove(request.user)
                comment_id.like.add(request.user)
                type = 2
            elif comment_id.like.filter(id=request.user.id).exists(): # თუ ლაიქი აქვს უკვე,ესეიგი ანლაიქი უნდა და წაშალე ლაიქი
                comment_id.like.remove(request.user)
                type = 0
            else: # არაფერი ეწინააღმდეგება ,უბრალოდ დაამატე ლაიქი
                comment_id.like.add(request.user)
                type = 1

            return JsonResponse({'info': "დალაიქდა!",'type':type}, status=200)
        else:
            return JsonResponse({'error':'მოხდა შეცდომა!'}, status=400)
    else:
        return JsonResponse({'error':"არაავტორიზებული მოთხოვნა!"},status=401)


def dislike_comment(request):
    if request.user.is_authenticated:
        try:
            comment_id = Comment.objects.get(id=request.POST.get('id',False))
        except (TypeError, ValueError, OverflowError,Comment.DoesNotExist,Comment.MultipleObjectsReturned):
            comment_id = None

        if comment_id and comment_id.user != request.user:

            if comment_id.like.filter(id=request.user.id).exists():
                comment_id.like.remove(request.user)
                comment_id.dislike.add(request.user)
                type = 2
            elif comment_id.dislike.filter(id=request.user.id).exists():
                comment_id.dislike.remove(request.user)
                type = 0
            else:
                comment_id.dislike.add(request.user)
                type = 1

            return JsonResponse({'info': "დადისლაიქდა!",'type':type}, status=200)
        else:
            return JsonResponse({'error':'მოხდა შეცდომა!'}, status=400)
    else:
        return JsonResponse({'error': "არაავტორიზებული მოთხოვნა!"}, status=401)


class ChangeEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and email_change_token.check_token(user, token):
            user.email = user.settings.new_email
            user.save()
            return redirect('profile')
        else:
            # invalid link
            return render(request, 'registration/invalid.html')