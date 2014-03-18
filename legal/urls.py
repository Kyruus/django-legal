from django.conf.urls import patterns, url
from legal.views import PrivacyPolicyView, TermsOfServiceView, TermsOfServiceAcceptView


urlpatterns = patterns(
    '',
    url(r'^privacy-policy/$', PrivacyPolicyView.as_view(), name='privacy_policy'),
    url(r'^terms-of-service/$', TermsOfServiceView.as_view(), name='tos'),
    url(r'terms-of-service-accept/$', TermsOfServiceAcceptView.as_view(), name='tos_accept'),
)
