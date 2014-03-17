from django.conf import settings

TOS_NAME = getattr(settings, 'LEGAL_TOS_NAME', 'tos')
