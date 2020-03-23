from django.http import HttpResponseRedirect

def anonymous_required(function=None,redirect_field_name='/account/profile'):
    """ Check that the user is NOT logged in. """

    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return HttpResponseRedirect(redirect_field_name)
            else:
                return view_func(request, *args, **kwargs)

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)