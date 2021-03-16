import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.db.models.expressions import Case, When
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import never_cache

from account.forms import SignUpForm, MyAuthenticationForm, CommentForm, \
    UpdateProfileForm, UpdateUsernameForm, EmailChangeForm, ShowProfileForm
from anime.models import Anime
from .models import Comment, Profile, Notification, Settings, Reply
from .tokens import email_change_token

ERROR = {'error': 'moxda shecdoma!'}

User = get_user_model()


def login_view(request):
    next_page = request.GET.get('next') or request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        form = MyAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'გამარჯობა, {}'.format(form.get_user()), extra_tags='welcome')
            return redirect(next_page)
        else:
            try:
                error = form.non_field_errors().as_data()[0].messages[0]
            except IndexError:
                error = "მოხდა კრიტიკული შეცდომა, გთხოვთ მიწეროთ ადმინისტრაციას დეტალებისთვის."
            messages.error(request, error, extra_tags='failedAuth')
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
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                login(request, user)

                # add ip field to settings
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(',')[-1].strip()
                else:
                    ip_address = request.META.get('REMOTE_ADDR')

                save_ip = Settings.objects.get(user_id=user.pk)
                save_ip.ip = ip_address
                save_ip.save()
                return redirect('profile')
        else:
            form = SignUpForm()
        return render(request, 'account/signup.html', {'register': form})
    else:
        return redirect('home')


def profile_view(request):
    if request.user.is_authenticated:
        user = User.objects.with_user_details().get(pk=request.user.pk)
        if request.method == 'POST':
            profile_form = UpdateProfileForm(request.POST, instance=user.profile)
            settings_form = ShowProfileForm(request.POST, instance=user.settings)
            if profile_form.is_valid() and settings_form.is_valid():
                settings_form.save()
                profile_form.save()
                return redirect('profile')
        else:
            profile_form = UpdateProfileForm(instance=user.profile)
            settings_form = ShowProfileForm(instance=user.settings)
        context = {
            'user': user,
            'p_form': profile_form,
            's_form': settings_form,
        }
        return render(request, 'account/profile.html', context)
    else:
        return redirect('home')


def profile_preview(request, id):
    user = get_object_or_404(User.objects.with_user_details(), pk=id)
    return render(request, 'account/profile_preview.html', {'user_profile': user})


def username_update(request):
    if request.user.is_authenticated and request.is_ajax() and request.method == "POST":
        username_form = UpdateUsernameForm(user=request.user, data=request.POST)
        if username_form.is_valid():
            username_form.save()
            return JsonResponse({'success': 'true',
                                 'time': datetime.datetime.timestamp(
                                     request.user.settings.username_updated + datetime.timedelta(days=7)),
                                 }, status=200)
        else:
            return JsonResponse({'success': 'false',
                                 'errors': username_form.errors['username']}, status=400)
    else:
        return JsonResponse({'status': 'false', 'info': 'moxda shecdoma!'}, status=400)


def avatar_update(request):
    if request.user.is_authenticated and request.is_ajax():
        if request.method == 'POST':
            avatar = request.FILES.get('data', None)
            if avatar:
                from PIL import Image
                check_avatar = Image.open(avatar)
                if check_avatar.format != "JPEG" or check_avatar.size[0] > 560 or check_avatar.size[1] > 560:
                    return JsonResponse({'info': 'არ აკმაყოფილებს პირობებს!'}, status=406)

                profile = request.user.profile
                settings = request.user.settings
                changed_avatar = settings.changed_avatar
                now = timezone.now()

                # settings update
                if changed_avatar != 0:
                    settings.avatar_updated = now
                settings.changed_avatar = F('changed_avatar') + 1
                settings.save()

                # uploading and saving
                avatar.name = str(request.user.pk) + '_{}_{}'.format(changed_avatar + 1, now.date()) + '.jpg'
                profile.avatar = avatar
                profile.save()

                return JsonResponse({'time': datetime.datetime.timestamp(
                    settings.avatar_updated + datetime.timedelta(days=3)),
                    'new_avatar': 'avatars/{}'.format(avatar.name),
                }, status=200)
            return JsonResponse(ERROR, status=400)
        return JsonResponse(ERROR, status=405)
    else:
        return redirect('home')


def avatar_delete(request):
    if request.user.is_authenticated and request.is_ajax():
        if request.method == 'DELETE':
            profile = Profile.objects.get(pk=request.user.pk)
            profile.avatar = 'no-avatar.jpg'
            profile.save()
            return JsonResponse({'success': True, 'info': 'ავატარი წაიშალა!'}, status=200)
        return JsonResponse(ERROR, status=405)
    return JsonResponse(ERROR, status=406)


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
        # TODO Async
        request.user.email_user(mail_subject, message)

        return JsonResponse({'success': 'true'}, status=200)
    else:
        return redirect('home')


@never_cache
def change_email_view(request, uidb64, token):
    if request.user.is_authenticated:
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None

        if user is not None and email_change_token.check_token(user, token):
            if user == request.user:
                if request.method == "POST":
                    email_form = EmailChangeForm(user=user, data=request.POST)
                    if email_form.is_valid():
                        email_form.save()
                        return redirect('profile')
                else:
                    email_form = EmailChangeForm(user=user)
                return render(request, 'registration/account_email_change_form.html', {'form': email_form})
            else:
                return redirect('profile')
        else:
            return render(request, 'registration/invalid.html')
    else:
        return redirect('home')


# COMMENT SYSTEM

def add_comment(request):
    if request.is_ajax() and request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                try:
                    anime = Anime.objects.get(id=request.POST.get('id', False))
                except (TypeError, ValueError, OverflowError, Anime.DoesNotExist):
                    anime = None

                if anime:
                    comment = form.save(commit=False)
                    comment.anime = anime
                    comment.user = request.user

                    comment.save()

                    response_data = {
                        'username': request.user.username,
                        'avatar': request.user.profile.avatar.name,
                        'user_id': request.user.id,
                        'user_active': request.user.is_active,
                        'comment_id': comment.id,
                        'editable': True,
                        'time': datetime.datetime.timestamp(comment.created),
                        'likes': 0,
                        'dislikes': 0
                    }

                    status = 200
                else:
                    response_data = {
                        'error': 'aseti anime bazashi ar aris!',
                    }
                    status = 404
                return JsonResponse(response_data, status=status)
            else:
                return JsonResponse(form.errors.get_json_data(), status=400)
        else:
            return JsonResponse({'error': "არაავტორიზებული მოთხოვნა!"}, status=401)
    else:
        return JsonResponse({'error': "არასწორი მოთხოვნა!"}, status=405)


def reply_comment(request):
    if request.is_ajax() and request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                try:
                    parent_comment = Comment.objects.get(id=int(request.POST.get('parent_id', False)))
                except (ValueError, Comment.DoesNotExist):
                    return JsonResponse({'error': 'ასეთი კომენტარი არ არსებობს!'}, status=404)

                try:
                    to_comment = Comment.objects.get(id=int(request.POST.get('replying_to_id', False)))
                except (ValueError, Comment.DoesNotExist):
                    to_comment = parent_comment

                reply_comment = form.save(commit=False)
                reply_comment.anime = parent_comment.anime
                reply_comment.parent = parent_comment
                reply_comment.user = request.user

                reply_comment.save()

                Reply.objects.create(
                    to_comment=to_comment,
                    reply_comment=reply_comment
                )

                return JsonResponse({
                    'username': request.user.username,
                    'avatar': request.user.profile.avatar.name,
                    'user_id': request.user.id,
                    'editable': True,
                    'user_active': request.user.is_active,
                    'comment_id': reply_comment.id,
                    'parent_id': reply_comment.parent.id,
                    'time': datetime.datetime.timestamp(reply_comment.created),
                    'likes': 0,
                    'dislikes': 0
                }, status=200)
            else:
                return JsonResponse(form.errors.get_json_data(), status=400)
        else:
            return JsonResponse({'error': "araavtorizebuli motxovna!"}, status=401)
    else:
        return JsonResponse({'error': "arasowri motxovna!"}, status=405)


def check_replies(request, id):
    if request.is_ajax():
        try:
            page = int(request.GET.get('skip', None))
        except ValueError:
            page = None

        if page is not None:
            paginator = Paginator(Comment.objects.filter(parent=id), 6)

            if paginator.num_pages >= page > 0:
                result = {'replies': [], 'availablePages': paginator.num_pages}
                for reply in paginator.get_page(page).object_list:
                    result['replies'].append(reply.get_reply_comment_info(request.user))
                return JsonResponse(result, status=200)
        return JsonResponse(ERROR, status=404)
    return JsonResponse(ERROR, status=405)


def more_comments(request, anime_id, page):

    parent = request.GET.get('parent', None)

    if parent and parent.isdecimal():
        comments = Comment.objects.annotates_related_objects(request.user).filter(
            Q(active=True) | Q(active_children_count__gte=1), parent__isnull=True, anime=anime_id).order_by(
            Case(
                When(id=parent, then=1),
                default=2,
            ),
            '-priority',
            '-id')
    else:
        comments = Comment.objects.annotates_related_objects(request.user).filter(
            Q(active=True) | Q(active_children_count__gte=1),
            parent__isnull=True, anime_id=anime_id)

    paginator = Paginator(comments, 6)

    if paginator.num_pages >= page:
        result = list()
        for comment in paginator.get_page(page).object_list:
            if comment.active:
                result.append(comment.get_more_comment_info(request.user))
            else:
                result.append(comment.get_deleted_comment_info())
        return JsonResponse(result, status=200, safe=False)
    else:
        return JsonResponse(ERROR, status=404)


def delete_comment(request, id):
    if request.is_ajax() and request.method == "DELETE":
        if request.user.is_authenticated:
            try:
                comment = Comment.objects.get(id=id)
            except Comment.DoesNotExist:
                comment = None

            if comment is not None:
                if request.user == comment.user:
                    comment.active = False
                    comment.save()

                    response_data = comment.get_deleted_comment_info()
                    status = 200
                else:
                    response_data = {'error': 'sxvis komentars ver washli!'}
                    status = 401
            else:
                response_data = {'error': 'aseti komentari ar arsebobs!'}
                status = 404

            return JsonResponse(response_data, status=status)
        else:
            return JsonResponse({'error': "araavtorizebuli motxovna!"}, status=401)
    else:
        return JsonResponse({'error': "araswori motxovna!"}, status=405)


def edit_comment(request):
    if request.is_ajax() and request.method == "POST":
        if request.user.is_authenticated:
            try:
                comment = Comment.objects.get(id=request.POST.get('id', False))
            except (TypeError, ValueError, OverflowError, Comment.DoesNotExist):
                return JsonResponse({'error': 'moxda shecdoma!'}, status=400)

            body = request.POST.get('body', None)

            if body and request.user == comment.user and comment.like.count() == 0 and \
                    comment.dislike.count() == 0 and comment.children.filter(active=True). \
                    exclude(user_id=request.user).count() == 0 and \
                    comment.replies.exclude(reply_comment__user=request.user).count() == 0 and comment.active:

                comment.body = body
                comment.created = timezone.now()
                comment.save()

                response_data = {
                    'success': True,
                    'time': datetime.datetime.timestamp(comment.created),
                }
                status = 200
            else:
                response_data = {
                    'error': 'moxda shecdoma!'
                }
                status = 400

            return JsonResponse(response_data, status=status)
        else:
            return JsonResponse({'error': "araavtorizebuli motxovna!"}, status=401)
    else:
        return JsonResponse({'error': "araswori motxovna!"}, status=405)


def like_comment(request):
    if request.user.is_authenticated:
        try:
            comment = Comment.objects.prefetch_related('like', 'dislike').get(id=request.POST.get('id', False))
        except (TypeError, ValueError, OverflowError, Comment.DoesNotExist):
            comment = None

        if comment and comment.user != request.user:

            if comment.dislike.filter(id=request.user.id).exists():  # თუ დისლაიქი აქვს კომს წაშალე დისლაქი და დაამატე ლაიქი
                comment.dislike.remove(request.user)
                comment.like.add(request.user)
                return JsonResponse({'type': 2}, status=200)
            elif comment.like.filter(
                    id=request.user.id).exists():  # თუ ლაიქი აქვს უკვე,ესეიგი ანლაიქი უნდა და წაშალე ლაიქი
                comment.like.remove(request.user)
                return JsonResponse({'type': 0}, status=200)
            else:  # არაფერი ეწინააღმდეგება ,უბრალოდ დაამატე ლაიქი
                comment.like.add(request.user)
                return JsonResponse({'type': 1}, status=200)

        else:
            return JsonResponse({'error': 'dafiqsirda shecdoma!'}, status=400)
    else:
        return JsonResponse({'error': "araavtorizebuli motxovna!"}, status=401)


def dislike_comment(request):
    if request.user.is_authenticated:
        try:
            comment = Comment.objects.prefetch_related('dislike', 'like').get(id=request.POST.get('id', False))
        except (TypeError, ValueError, OverflowError, Comment.DoesNotExist):
            return JsonResponse({'error': 'dafiqsirda shecdoma!'}, status=400)

        if comment.user != request.user:

            if comment.like.filter(id=request.user.id).exists():
                comment.like.remove(request.user)
                comment.dislike.add(request.user)
                return JsonResponse({'type': 2}, status=200)
            elif comment.dislike.filter(id=request.user.id).exists():
                comment.dislike.remove(request.user)
                return JsonResponse({'type': 0}, status=200)
            else:
                comment.dislike.add(request.user)
                return JsonResponse({'type': 1}, status=200)
    return JsonResponse({'error': "araavtorizebuli motxovna!"}, status=401)


def check_notification_reply(request):
    if request.user.is_authenticated:
        notifications = request.user.notifications
        # TODO try raw sql
        reply = notifications.filter(content_type__model='reply', seen=False).count()
        admin_message = notifications.filter(content_type__model='message', seen=False).count()

        replies = notifications.filter(content_type__model='reply').prefetch_related(
            'content_object').values(
            'id', 'reply__to_comment', 'reply__to_comment__body', 'reply__reply_comment__created',
            'reply__to_comment__anime__slug', 'reply__to_comment__parent_id', 'seen').order_by(
            '-reply__reply_comment__created')

        return render(request, 'account/notifications.html',
                      {'total': {'reply': reply, 'admin_message': admin_message}, 'replies': replies})
    return redirect('home')


def check_notification_message(request):
    if request.user.is_authenticated:
        notifications = request.user.notifications

        reply = notifications.filter(content_type__model='reply', seen=False).count()
        admin_message = notifications.filter(content_type__model='message', seen=False).count()

        message = notifications.filter(content_type__model='message').prefetch_related('content_object').values(
            'id', 'message__subject', 'message__id', 'message__created', 'seen') \
            .order_by('-message__created')

        return render(request, 'account/message.html',
                      {'total': {'reply': reply, 'admin_message': admin_message}, 'msgs': message})
    return redirect('home')


def delete_notification(request, id):
    if request.method == "DELETE":
        if request.user.is_authenticated:
            try:
                Notification.objects.get(user_id=request.user, id=id).delete()
            except Notification.DoesNotExist:
                return JsonResponse({'error': "ver moizebna!"}, status=404)

            return JsonResponse({'info': "waishala"}, status=200)
        return JsonResponse({'error': "araavtorizebuli motxovna!"}, status=401)
    return JsonResponse({'error': "araswori motxovna!"}, status=405)


def delete_all_notification_by_content(request, content):
    if request.method == "DELETE":
        if request.user.is_authenticated:
            try:
                Notification.objects.filter(user_id=request.user, content_type__model=content).delete()
            except Notification.DoesNotExist:
                return JsonResponse({'error': "ver moizebna!"}, status=404)

            return JsonResponse({'info': "waishala"}, status=200)
        return JsonResponse({'error': "araavtorizebuli motxovna!"}, status=401)
    return JsonResponse({'error': "araswori motxovna!"}, status=405)
