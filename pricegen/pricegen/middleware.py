# coding=utf-8

from django.http import HttpResponseRedirect

from django.conf import settings
import re

exempt_urls = [re.compile('^' + re.escape(url.lstrip('/')), flags=re.I) \
                for url in (
                    settings.LOGOUT_URL,
                    settings.LOGIN_URL,
                    'not_implemented',
                    'favicon.ico',
                )
]

class LoginRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        path = request.path_info.lstrip('/')
        if any(m.match(path) for m in exempt_urls):
            pass
        elif not request.user.is_authenticated:
            next = '' if not path or exempt_urls[0].match(path) else '?redirectUrl='+request.build_absolute_uri()
            return HttpResponseRedirect(settings.LOGIN_URL+next)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
