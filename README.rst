django-legal
============

This Django app adds support for versioned terms of service.

Installation
------------
1. Add ``legal`` to your ``INSTALLED_APPS`` setting.
2. *(Optional)* Add a new setting: ``LEGAL_TOS_NAME = 'terms_of_service'``
3. Update ``urls.py`` with the following::

    url(r'^legal/', include('legal.urls')),

4. Create a new Agreement and AgreementVersion (ideally via data migration)::

    from django.utils import timezone
    from legal.models import Agreement, AgreementVersion

    name = 'tos' # Change this to the value of `LEGAL_TOS_NAME` if you overrode it.
    agreement = Agreement.objects.create(name=name)
    content = "<load data from a file if you don't want a huge block of text in your script>"
    AgreementVersion.objects.create(agreement=agreement, date=timezone.now(), content=content)


Testing
-------
A modified ``manage.py`` and Django settings file are included to test this app::

    $ python manage.py test
