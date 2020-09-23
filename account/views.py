import datetime

from django.contrib.auth.backends import UserModel
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import never_cache

from .tokens import email_change_token
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from account.forms import SignUpForm, MyAuthenticationForm, CommentForm,\
    UpdateProfileForm, UpdateUsernameForm, EmailChangeForm,ShowProfileForm
from anime.models import Anime
from .models import Comment, Profile, Notification, Settings

ERROR = {'error':'moxda shecdoma!'}

def login_view(request):
    next_page = request.GET.get('next') or request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        form = MyAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request,'გამარჯობა, {}'.format(form.get_user()),extra_tags='welcome')
            return redirect(next_page)
        else:
            messages.error(request, 'ნიკი ან პაროლი არასწორია. თავიდან სცადეთ!',extra_tags='failedAuth')
            return redirect(next_page)
    else:
        return redirect(next_page)

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

                # add ip field to settings
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

                if x_forwarded_for:
                    ipaddress = x_forwarded_for.split(',')[-1].strip()
                else:
                    ipaddress = request.META.get('REMOTE_ADDR')

                save_ip = Settings.objects.get(user_id=user.pk)
                save_ip.ip = ipaddress
                save_ip.save()
                return redirect('profile')
        else:
            form = SignUpForm()
        return render(request, 'account/signup.html', {'register': form})
    else:
        return redirect('home')

def profile_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            profile_form = UpdateProfileForm(request.POST,instance=request.user.profile)
            settings_form = ShowProfileForm(request.POST,instance=request.user.settings)
            if profile_form.is_valid() and settings_form.is_valid():
                settings_form.save()
                profile_form.save()
                return redirect('profile')
        else:
            profile_form = UpdateProfileForm(instance=request.user.profile)
            settings_form = ShowProfileForm(instance=request.user.settings)
        context = {
            'p_form':profile_form,
            's_form':settings_form,
        }
        return render(request, 'account/profile.html', context)
    else:
        return redirect('home')


def profile_preview(request,id):
    if isinstance(id,int):
        user = get_object_or_404(User.objects.select_related('profile','settings'),pk=id)
    else:
        return Http404
    return render(request,'account/profile_preview.html',{'profileuser':user})


def username_update(request):
    if request.user.is_authenticated and request.is_ajax() and request.method == "POST":
        username_form = UpdateUsernameForm(user=request.user,data=request.POST)
        if username_form.is_valid():
            username_form.save()
            return JsonResponse({'success':'true',
                                 'time': datetime.datetime.timestamp(
                                     request.user.settings.username_updated + datetime.timedelta(days=7)),
                                 },status=200)
        else:
            return JsonResponse({'success':'false',
                                 'errors':username_form.errors['username']}, status=400)
    else:
        return JsonResponse({'status':'false','info':'moxda shecdoma!'},status=400)

def avatar_update(request):
    if request.user.is_authenticated and request.is_ajax():
        if request.method == 'POST':
            is_type = request.POST.get('type',None)
            if is_type is not None:
                profile = Profile.objects.get(pk=request.pk)
                profile.avatar = 'no-avatar.jpg'
                profile.save()
                return JsonResponse({'success': True,'info':'ავატარი წაიშალა!'}, status=200)
            avatar = request.FILES.get('data',None)
            if avatar:
                from PIL import Image
                check_avatar = Image.open(avatar)
                if check_avatar.format!="JPEG" or check_avatar.size[0] > 200 or check_avatar.size[1] > 200:
                    return JsonResponse({'success':'false','info':'არ აკმაყოფილებს პირობებს!'})

                profile = request.user.profile
                settings = request.user.settings

                # settings update
                settings.avatar_updated = timezone.now()
                settings.save()

                # uploading and saving
                avatar.name = str(request.user.pk) + '_{}'.format(settings.avatar_updated.date()) + '.jpg'
                profile.avatar = request.FILES.get('data')
                profile.save()

                return JsonResponse({'success':True,
                                     'time':datetime.datetime.timestamp(settings.avatar_updated+datetime.timedelta(days=3)),
                                     'new_avatar':'avatars/{}'.format(avatar.name),
                                     }, status=200)
            else:
                return JsonResponse({'success': False,'info':'moxda shecdoma!'},status=400)

        return render(request, 'account/profile.html')
    else:
        return redirect('home')



def change_email_request_view(request):
    if request.user.is_authenticated and request.is_ajax():
        from django.template.loader import render_to_string
        current_site = get_current_site(request)
        mail_subject = 'Email-ის შეცვლა'
        message = render_to_string('registration/account_email_change_email.html', {
            'user': request.user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(request.user.pk)).decode(),
            'token': email_change_token.make_token(request.user),
        })
        request.user.email_user(mail_subject,message)
        return JsonResponse({'success':'true'},status=200)
    else:
        return redirect('home')



@never_cache
def change_email_view(request,uidb64,token):
    if request.user.is_authenticated:
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist,ValidationError):
            user = None

        if user is not None and email_change_token.check_token(user,token):
            if user == request.user:
                if request.method == "POST":
                    email_form = EmailChangeForm(user=user,data=request.POST)
                    if email_form.is_valid():
                        email_form.save()
                        return redirect('profile')
                else:
                    email_form = EmailChangeForm(user=user)
                return render(request,'registration/account_email_change_form.html',{'form':email_form})
            else:
                return redirect('profile')
        else:
            return render(request,'registration/invalid.html')
    else:
        return redirect('home')

# COMMENT SYSTEM

def add_comment(request):
    if request.is_ajax() and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                parent_id = int(request.POST.get('parent_id', False))
                parent_comment = Comment.objects.get(id=parent_id)
            except (TypeError, ValueError, OverflowError,Comment.DoesNotExist):
                parent_comment = None

            if parent_comment:

                #send notification to replying_comment_author
                try:
                    replying_to_id = int(request.POST.get('replying_to_id', False))
                    replying_to_comment_obj = Comment.objects.get(id=replying_to_id)
                except (TypeError, ValueError, OverflowError,Comment.DoesNotExist):
                    replying_to_comment_obj = None

                request_user = request.user

                if replying_to_comment_obj:
                    replying_comment_author = replying_to_comment_obj.user_id
                else:
                    replying_to_comment_obj = parent_comment
                    replying_comment_author = parent_comment.user_id

                reply_comment = form.save(commit=False)
                reply_comment.anime = parent_comment.anime
                reply_comment.parent = parent_comment
                reply_comment.user = request_user

                reply_comment.save()

                if not replying_comment_author == request_user.id:
                    Notification.objects.create(reply_comment_id=replying_to_comment_obj.id,
                                            user_id=replying_comment_author,
                                            comment_id=reply_comment.id)

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
                    # if request.POST.get('spoiler', False) == 'true':
                    #     comment.spoiler = True
                    # else:
                    #     comment.spoiler = False
                    comment.save()

                    response_data = {
                        'username':request.user.username,
                        'avatar':request.user.profile.avatar.name,
                        'user_id':request.user.id,
                        'comment_id':comment.id,
                        # 'has_spoiler': comment.spoiler,
                    }

                    status = 200
                else:
                    response_data = {
                        'error':'aseti anime ID bazashi ar aris!',
                    }
                    status = 400
            return JsonResponse(response_data,status=status)

        else:
            return JsonResponse(ERROR, status=400)
    else:
        return JsonResponse({'error':"araavtorizebuli motxovna!"},status=401)


def check_replies(request,int):
    if request.is_ajax():
        try:
            replies = Comment.objects.filter(parent=int)
        except (Comment.DoesNotExist,Comment.MultipleObjectsReturned):
            replies = None

        if replies:
            result = list()
            replies_iterator = replies.iterator()
            for reply in replies_iterator:
                result.append(reply.get_reply_comment_info(request.user.pk))
            return JsonResponse(result, status=200,safe=False)
        else:
            return JsonResponse({'error':'repliebi ar arsebobs!'},status=400)
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
                    'info': 'komentari waishala!'
                }
                status = 200
            else:
                response_data = {
                    'error': 'sxvis komentars ver washli!'
                }
                status = 401
        else:
            response_data = {
                'error':'aseti komentari ar arsebobs!'
            }
            status = 400

        return JsonResponse(response_data,status=status)
    else:
        return JsonResponse({'error':"araavtorizebuli motxovna!"},status=401)


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
                    'info': 'komentari sheicvala!',
                    'time':datetime.datetime.timestamp(comment_id.created),
                }
                status = 200
            else:
                response_data = {
                    'error': 'moxda shecdoma!'
                }
                status = 401 if request.user.id != comment_id.user.id else 400
        else:
            response_data = {
                'error':'moxda shecdoma!'
            }
            status = 400

        return JsonResponse(response_data,status=status)
    else:
        return JsonResponse({'error':"araavtorizebuli motxovna!"},status=401)


def like_comment(request):
    if request.user.is_authenticated:
        try:
            comment_id = Comment.objects.prefetch_related('like','dislike').get(id=request.POST.get('id',False))
        except (TypeError, ValueError, OverflowError,Comment.DoesNotExist):
            comment_id = None

        if comment_id and comment_id.user != request.user:

            if comment_id.dislike.filter(id=request.user.id).exists(): # თუ დისლაიქი აქვს კომს წაშალე დისლაქი და დაამატე ლაიქი
                comment_id.dislike.remove(request.user)
                comment_id.like.add(request.user)
                return JsonResponse({'type': 2}, status=200)
            elif comment_id.like.filter(id=request.user.id).exists(): # თუ ლაიქი აქვს უკვე,ესეიგი ანლაიქი უნდა და წაშალე ლაიქი
                comment_id.like.remove(request.user)
                return JsonResponse({'type': 0}, status=200)
            else: # არაფერი ეწინააღმდეგება ,უბრალოდ დაამატე ლაიქი
                comment_id.like.add(request.user)
                return JsonResponse({'type': 1}, status=200)

            # return JsonResponse({'info': "like"}, status=200)
        else:
            return JsonResponse({'error':'dafiqsirda shecdoma!'}, status=400)
    else:
        return JsonResponse({'error':"araavtorizebuli motxovna!"},status=401)


def dislike_comment(request):
    if request.user.is_authenticated:
        try:
            comment_id = Comment.objects.prefetch_related('dislike','like').get(id=request.POST.get('id',False))
        except (TypeError, ValueError, OverflowError,Comment.DoesNotExist,Comment.MultipleObjectsReturned):
            comment_id = None

        if comment_id and comment_id.user != request.user:

            if comment_id.like.filter(id=request.user.id).exists():
                comment_id.like.remove(request.user)
                comment_id.dislike.add(request.user)
                return JsonResponse({'type': 2}, status=200)
            elif comment_id.dislike.filter(id=request.user.id).exists():
                comment_id.dislike.remove(request.user)
                return JsonResponse({'type': 0}, status=200)
            else:
                comment_id.dislike.add(request.user)
                return JsonResponse({'type': 1}, status=200)
        else:
            return JsonResponse({'error':'dafiqsirda shecdoma!'}, status=400)
    else:
        return JsonResponse({'error': "araavtorizebuli motxovna!"}, status=401)


def check_notification(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.select_related('user','reply_comment','comment').\
            filter(user_id=request.user).values_list(
            'reply_comment_id','reply_comment__body','comment__created',
            'comment__anime__slug','reply_comment__parent','id'
        )
        notif_exists = notifications.exists()
        context = {
            'exists':notif_exists
        }

        if notif_exists:
            context['notifications'] = notifications
        return render(request, 'account/notifications.html',context)
    else:
        return redirect('home')