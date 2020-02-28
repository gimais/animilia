from django.http import JsonResponse


class AjaxCommentFormMixin(object):
    def form_invalid(self, form):
        response = super(AjaxCommentFormMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxCommentFormMixin, self).form_valid(form)

        # instance = form.save(commit=False)
        # instance.user = self.request.user
        # instance.anime = self.request.slug
        # instance.save()
        print(self.request.user)
        # print(self.request.anime)
        print(self.request.body)
        print(self.request.created)

        if self.request.is_ajax():
            data = {
                'username': str(self.request.user),
                'avatar':'aq iqneba avataris linki',
            }
            return JsonResponse(data)
        else:
            return response
