from django.conf.urls import patterns, url, include


urlpatterns = patterns(
    '',
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^legal/', include('legal.urls')),
)
