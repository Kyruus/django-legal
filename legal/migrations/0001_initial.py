# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


try:
    from django.contrib.auth import get_user_model

    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.module_name)


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'Agreement'
        db.create_table('legal_agreement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, db_index=True)),
        ))
        db.send_create_signal('legal', ['Agreement'])

        # Adding model 'AgreementVersion'
        db.create_table('legal_agreementversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('agreement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legal.Agreement'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('legal', ['AgreementVersion'])

        # Adding unique constraint on 'AgreementVersion', fields ['agreement', 'date']
        db.create_unique('legal_agreementversion', ['agreement_id', 'date'])

        # Adding model 'AgreementAcceptance'
        db.create_table('legal_agreementacceptance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[user_orm_label])),
            ('agreement_version',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legal.AgreementVersion'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('legal', ['AgreementAcceptance'])

        # Adding unique constraint on 'AgreementAcceptance', fields ['user', 'agreement_version', 'date']
        db.create_unique('legal_agreementacceptance', ['user_id', 'agreement_version_id', 'date'])


    def backwards(self, orm):
        # Removing unique constraint on 'AgreementAcceptance', fields ['user', 'agreement_version', 'date']
        db.delete_unique('legal_agreementacceptance', ['user_id', 'agreement_version_id', 'date'])

        # Removing unique constraint on 'AgreementVersion', fields ['agreement', 'date']
        db.delete_unique('legal_agreementversion', ['agreement_id', 'date'])

        # Deleting model 'Agreement'
        db.delete_table('legal_agreement')

        # Deleting model 'AgreementVersion'
        db.delete_table('legal_agreementversion')

        # Deleting model 'AgreementAcceptance'
        db.delete_table('legal_agreementacceptance')


    models = {
        user_model_label: {
            'Meta': {
                'object_name': User.__name__,
                'db_table': "'%s'" % User._meta.db_table
            },
            User._meta.pk.attname: (
                'django.db.models.fields.AutoField', [],
                {'primary_key': 'True',
                 'db_column': "'%s'" % User._meta.pk.column}
            ),
        },
        'legal.agreement': {
            'Meta': {'object_name': 'Agreement'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': (
                'django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'legal.agreementacceptance': {
            'Meta': {'ordering': "['-date']", 'unique_together': "(('user', 'agreement_version', 'date'),)",
                     'object_name': 'AgreementAcceptance'},
            'agreement_version': (
                'django.db.models.fields.related.ForeignKey', [], {'to': "orm['legal.AgreementVersion']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['%s']" % user_orm_label})
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

    complete_apps = ['legal']