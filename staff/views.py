from django.http import JsonResponse, HttpResponse

from account.models import Profile

# Create your views here.
from feedback.models import Message

ERROR = {'error': 'moxda shecdoma!'}


def avatar_delete(request, id):
    if request.user.is_staff and request.is_ajax():
        if request.method == 'DELETE':
            profile = Profile.objects.get(pk=id)
            profile.avatar = 'no-avatar.jpg'
            profile.save()
            return JsonResponse({'success': True, 'info': 'ავატარი წაიშალა!'}, status=200)
        return JsonResponse(ERROR, status=405)
    return JsonResponse(ERROR, status=406)


def show_info(request, id):
    if request.user.is_staff and request.is_ajax():
        if request.method == 'GET':
            profile = Profile.objects.select_related('user__settings').get(pk=id)

            user_info = {
                "email": profile.user.email,
                "last_login": profile.user.last_login,
                "registration": profile.user.date_joined,
                "gender": profile.gender,
                "birth": profile.birth,
                "show_birth": profile.user.settings.show_birth,
                "show_gender": profile.user.settings.show_gender,
                "avatar_updated": profile.user.settings.avatar_updated,
                "username_updated": profile.user.settings.username_updated
            }

            return JsonResponse(user_info, status=200)
        return JsonResponse(ERROR, status=405)
    return JsonResponse(ERROR, status=406)


def send_message(request, user):
    if request.user.is_staff and request.is_ajax():
        if request.method == 'POST':
            Message.objects.create(to_user_id=user, subject=request.POST['subject'], body=request.POST['body'])
            return HttpResponse(status=200)
        return JsonResponse(ERROR, status=405)
    return JsonResponse(ERROR, status=406)