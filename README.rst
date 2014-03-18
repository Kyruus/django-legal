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

    # -*- coding: utf-8 -*-
    import os
    from south.v2 import DataMigration

    # This should be the same value as LEGAL_TOS_NAME (if you overrode it)
    AGREEMENT_NAME = 'tos'


    class Migration(DataMigration):
        def forwards(self, orm):
            agreement, created = orm['legal.Agreement'].objects.get_or_create(name=AGREEMENT_NAME)

            # This file should live in the same directory as the migration
            f = open('%s/tos_content_2013_08_01.html' % os.path.dirname(__file__), 'r')
            orm['legal.AgreementVersion'].objects.create(agreement=agreement, date='2013-08-01', content=f.read())

        def backwards(self, orm):
            agreement = orm['legal.Agreement'].objects.get(name=AGREEMENT_NAME)
            agreement.delete()

        models = {
            'legal.agreement': {
                'Meta': {'object_name': 'Agreement'},
                'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
                'name': (
                    'django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
            },
            'legal.agreementversion': {
                'Meta': {'ordering': "['-date']", 'unique_together': "(('agreement', 'date'),)",
                         'object_name': 'AgreementVersion'},
                'agreement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['legal.Agreement']"}),
                'content': ('django.db.models.fields.TextField', [], {}),
                'date': ('django.db.models.fields.DateTimeField', [], {}),
                'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
            }
        }

        # Change this to be the name of the app where the migration lives
        complete_apps = ['my-app']
        symmetrical = True



Testing
-------
A modified ``manage.py`` and Django settings file are included to test this app::

    $ python manage.py test
