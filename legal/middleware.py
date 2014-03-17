import urllib
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from legal import TOS_NAME
from legal.models import Agreement


class TermsOfServiceAcceptanceMiddleware(object):
    def process_request(self, request):
        tos = Agreement.objects.get(name=TOS_NAME)
        tos_accept_path = reverse('tos_accept')

        if not tos.user_accepted(request.user) and request.path != tos_accept_path:
            next = request.path
            if request.GET:
                next += '?%s' % urllib.urlencode(request.GET)
            params = {'next': next}
            return redirect(tos_accept_path + '?%s' % urllib.urlencode(params))
