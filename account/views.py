from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from account.forms import SignUpForm, MyAuthenticationForm, CommentForm
from anime.models import Anime
from .models import Comment


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
        messages.error(request,'მოხდა შეცდომა!',extra_tags='error')
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
        messages.warning(request,'{}, თქვენ უკვე რეგისტრირებული ხართ!'.format(request.user.username),extra_tags='registered')
        return redirect('home')


def profile_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        return render(request,'account/profile.html',{'username':username})
    else:
        messages.error(request,'მოხდა შეცდომა,თქვენ არ ხართ ავტორიზებული!',extra_tags='nonAuth')
        return redirect('home')


# COMMENT SYSTEM

def add_comment(request):
    if request.is_ajax() and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None

            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                anime = Anime.objects.get(id=parent_comment.anime.id)

                reply_comment = form.save(commit=False)
                reply_comment.anime = anime
                reply_comment.parent = Comment.objects.get(id=parent_id)
                reply_comment.user = request.user
                reply_comment.save()

                response_data = {
                    'username':request.user.username,
                    'avatar':'avataris surati!',
                    'user_id':request.user.id, # ar washalooo ? edit da remove functiebistvis rom daadasturos js-shi
                    'comment_id':reply_comment.id,
                }
                status = 200
            else:
                try:
                    anime = Anime.objects.get(id=request.POST['id'])
                except Anime.DoesNotExist:
                    anime = None

                if anime:
                    comment = form.save(commit=False)
                    comment.anime = anime
                    comment.user = request.user
                    comment.save()

                    response_data = {
                        'username':request.user.username,
                        'avatar':'avataris surati!',
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
            return JsonResponse({'error':'მოხდა შეცდომა!'}, status=400)
    else:
        return JsonResponse({'error':"არაავტორიზებული მოთხოვნა!"},status=401)


def check_comments(request,int):
    if request.is_ajax():
        try:
            replies = Comment.objects.filter(parent=int)
        except Comment.DoesNotExist:
            replies = None

        if replies:
            result = list()
            for reply in replies:
                result.append(reply.get_reply_comment_info())
            return JsonResponse(result, status=200,safe=False)
        else:
            return JsonResponse({'error':'პასუხები არ არსებობს!'},status=400)
    return JsonResponse({'error': 'მოხდა შეცდომა!'}, status=400)


def delete_comment(request):
    if request.user.is_authenticated:
        try:
            comment_id = Comment.objects.get(id=request.POST['id'])
        except Comment.DoesNotExist:
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
            comment_id = Comment.objects.get(id=request.POST['id'])
            body = request.POST['id']
        except Exception as e:
            print(e)
            comment_id = None
            body = None

        if comment_id and body:
            if request.user == comment_id.user and comment_id.like.count() == 0 and \
                    comment_id.dislike.count() == 0 and comment_id.active:

                # comment_id.body = body
                # comment_id.save()

                response_data = {
                    'info': 'კომენტარი შეიცვალა!'
                }
                status = 200
            else:
                response_data = {
                    'error': 'მოხდა შეცდომა!'
                }
                status = 400
        else:
            response_data = {
                'error':'მოხდა შეცდომა!'
            }
            status = 401 if request.user!=comment_id.user else 400

        return JsonResponse(response_data,status=status)
    else:
        return JsonResponse({'error':"არაავტორიზებული მოთხოვნა!"},status=401)


def like_comment(request):
    if request.user.is_authenticated:
        try:
            comment_id = Comment.objects.get(id=request.POST['id'])
        except Comment.DoesNotExist:
            comment_id = None

        if comment_id and comment_id.user != request.user:

            if comment_id.like.filter(id=request.user.id).exists():
                comment_id.like.remove(request.user)
            else:
                comment_id.like.add(request.user)

            return JsonResponse({'info': "დალაიქდა!"}, status=200)
        else:
            return JsonResponse({'error': "მოხდა შეცდომა!"}, status=400)
    else:
        return JsonResponse({'error':"არაავტორიზებული მოთხოვნა!"},status=401)


def dislike_comment(request):
    if request.user.is_authenticated:
        try:
            comment_id = Comment.objects.get(id=request.POST['id'])
        except Comment.DoesNotExist:
            comment_id = None

        if comment_id and comment_id.user != request.user:

            if comment_id.dislike.filter(id=request.user.id).exists():
                comment_id.dislike.remove(request.user)
            else:
                comment_id.dislike.add(request.user)

            return JsonResponse({'info': "დადისლაიქდა!"}, status=200)
        else:
            return JsonResponse({'error': "მოხდა შეცდომა!"}, status=400)
    else:
        return JsonResponse({'error': "არაავტორიზებული მოთხოვნა!"}, status=401)