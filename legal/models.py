from django.conf import settings
from django.db import models
from legal.exceptions import NoVersionException

auth_user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Agreement(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.name

    @property
    def versions(self):
        """
        Returns all versions of this agreement.
        """
        return AgreementVersion.objects.filter(agreement=self)

    @property
    def current_version(self):
        """
        Returns the latest AgreementVersion for this Agreement. If none exists, raises NoVersionException.
        """
        versions = self.versions
        if versions:
            return versions[0]

        raise NoVersionException

    def user_accepted(self, user):
        current = self.current_version
        if not current:
            return False

        return AgreementAcceptance.objects.filter(user=user, agreement_version=current).exists()

    def accept(self, user):
        acceptance = AgreementAcceptance(agreement_version=self.current_version, user=user)
        acceptance.save()

    @property
    def date(self):
        return self.current_version.date

    @property
    def content(self):
        return self.current_version.content


class AgreementVersion(models.Model):
    agreement = models.ForeignKey(Agreement, db_index=True)
    date = models.DateTimeField()
    content = models.TextField()

    def __str__(self):
        return '%s published on %s' % (self.agreement.name, self.date)

    class Meta:
        unique_together = ('agreement', 'date')
        ordering = ["-date"]


class AgreementAcceptance(models.Model):
    user = models.ForeignKey(auth_user_model)
    agreement_version = models.ForeignKey(AgreementVersion)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s accepted %s (%s) on %s' % (
            self.user, self.agreement_version.agreement.name, self.agreement_version.date, self.date)

    class Meta:
        unique_together = ('user', 'agreement_version', 'date')
        ordering = ["-date"]
