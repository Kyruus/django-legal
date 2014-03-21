import urllib.parse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from legal import TOS_NAME
from legal.models import Agreement


class PrivacyPolicyView(TemplateView):
    template_name = 'legal/privacy.html'


class TermsOfServiceView(TemplateView):
    template_name = 'legal/tos.html'

    def get_context_data(self, **kwargs):
        context = super(TermsOfServiceView, self).get_context_data(**kwargs)
        context['tos'] = Agreement.objects.get(name=TOS_NAME)
        return context


class TermsOfServiceAcceptView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TermsOfServiceAcceptView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        tos = Agreement.objects.get(name=TOS_NAME).current_version
        return render(request, 'legal/tos_accept.html',
                      {'next': request.GET.get('next'), 'tos': tos, 'logout_url': settings.LOGOUT_URL})

    def post(self, request, *args, **kwargs):
        # Get the proper redirect location
        redirect_to = request.REQUEST.get('next', '/')
        netloc = urllib.parse.urlparse(redirect_to)[1]

        if netloc and netloc != request.get_host():
            redirect_to = '/'

        # Accept the agreement
        tos_agreement = Agreement.objects.get(name=TOS_NAME)
        tos_agreement.accept(request.user)

        # Redirect
        return HttpResponseRedirect(redirect_to)
