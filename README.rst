django-legal
============

This Django app adds support for versioned terms of service.

Installation
------------
  1. Add `legal` to your `INSTALLED_APPS` setting.
  2. (Optional) Add a new setting: `LEGAL_TOS_NAME = 'terms_of_service'`


Testing
-------
A modified `manage.py` and Django settings file are included to test this app.

    $ python manage.py test
