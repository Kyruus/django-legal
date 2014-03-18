import urllib
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, resolve_url
from legal import TOS_NAME
from legal.models import Agreement


class TermsOfServiceAcceptanceMiddleware(object):
    def process_request(self, request):
        tos = Agreement.objects.get(name=TOS_NAME)
        tos_accept_path = reverse_lazy('tos_accept')
        ignored_paths = [tos_accept_path, resolve_url(settings.LOGIN_URL), resolve_url(settings.LOGOUT_URL),
                         reverse_lazy('tos'), reverse_lazy('privacy_policy')]

        user = request.user
        if user.is_authenticated():
            if not tos.user_accepted(user) and request.path not in ignored_paths:
                next = request.path
                if request.GET:
                    next += '?%s' % urllib.urlencode(request.GET)
                params = {'next': next}
                return redirect(tos_accept_path + '?%s' % urllib.urlencode(params))
