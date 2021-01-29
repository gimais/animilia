from django.http import JsonResponse

from account.models import Profile

# Create your views here.

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
