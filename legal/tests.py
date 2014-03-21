import datetime
import random
import string
import urllib.request, urllib.parse, urllib.error
import urllib.parse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.test import TestCase, RequestFactory
from legal import TOS_NAME
from legal.middleware import TermsOfServiceAcceptanceMiddleware
from legal.models import *

ONE_DAY = datetime.timedelta(days=1)
current_datetime = datetime.datetime(2012, 1, 1)
PASSWORD = 'password'


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def get_user():
    username = 'test_user_%s' % id_generator()
    user = User.objects.create_user(username, email='%s@example.com' % username, password=PASSWORD)
    return user


def get_datetime():
    global current_datetime
    current_datetime += ONE_DAY
    return current_datetime


def get_agreement_version(agreement, save=True):
    av = AgreementVersion(agreement=agreement, date=get_datetime(), content=id_generator())
    if save:
        av.save()
    return av


class ModelsTest(TestCase):
    def setUp(self):
        self.agreement = Agreement.objects.create(name='test_agreement')

    def test_agreement_acceptance_auto_date_prevents_conflict(self):
        user = get_user()

        version1 = get_agreement_version(self.agreement)

        acceptance = AgreementAcceptance(user=user, agreement_version=version1, date='2012-04-01')
        acceptance.save()

        acceptance2 = AgreementAcceptance(user=user, agreement_version=version1, date='2012-04-01')
        acceptance2.save()

    def test_agreement_acceptance(self):
        """
        Tests that a user has signed the latest version of an agreement
        """
        user = get_user()

        # User cannot accept agreement with no versions
        self.assertRaises(NoVersionException, self.agreement.accept, user)
        self.assertRaises(NoVersionException, self.agreement.user_accepted, user)

        # Return True if the only version has been accepted
        version1 = get_agreement_version(self.agreement)
        self.agreement.accept(user)
        self.assertTrue(self.agreement.user_accepted(user))

        # Return False if latest version has not been accepted
        version2 = get_agreement_version(self.agreement)
        self.assertFalse(self.agreement.user_accepted(user))

        # Return True after accepting latest version
        self.agreement.accept(user)
        self.assertTrue(self.agreement.user_accepted(user))

        # Return True if latest version accepted, but not earlier version(s)
        user2 = get_user()
        self.assertFalse(self.agreement.user_accepted(user2))
        self.agreement.accept(user2)
        self.assertTrue(self.agreement.user_accepted(user2))

    def test_agreement_version_conflict(self):
        version1 = get_agreement_version(self.agreement)

        version2 = get_agreement_version(self.agreement, False)
        version2.date = version1.date

        # Calling save() throws an IntegrityError that is never caught, so just validate the model instead.
        self.assertRaises(ValidationError, version2.full_clean)

    def test_agreement_versions(self):
        self.assertFalse(self.agreement.versions, 'Agreement.versions should return [] for an agreement with no versions.')

        version1 = get_agreement_version(self.agreement)
        self.assertEqual(self.agreement.versions[0], version1, 'Agreement.versions should contain version1')

    def test_agreement_current_version(self):
        """
        Tests retrieval of the latest version of an agreement.
        """
        try:
            self.agreement.current_version
        except NoVersionException:
            pass
        except:
            raise self.fail(
                'Agreement.current_version should raise a NoVersionException when called for an Agreement with no versions.')

        version1 = get_agreement_version(self.agreement)
        self.assertEqual(self.agreement.current_version, version1, 'Incorrect first version.')

        version2 = get_agreement_version(self.agreement)
        self.assertEqual(self.agreement.current_version, version2, 'Incorrect second version.')

    def test_agreement_date_and_content(self):
        version1 = get_agreement_version(self.agreement)

        self.assertEqual(self.agreement.content, version1.content,
                         'Agreement.content should return the content of the latest version.')
        self.assertEqual(self.agreement.date, version1.date,
                         'Agreement.date should return the date of the latest version.')

        version2 = get_agreement_version(self.agreement)
        self.assertEqual(self.agreement.content, version2.content,
                         'Agreement.content should return the content of the latest version.')
        self.assertEqual(self.agreement.date, version2.date,
                         'Agreement.date should return the date of the latest version.')


class TermsOfServiceAcceptViewTests(TestCase):
    def get_and_login_user(self):
        user = get_user()
        if not self.client.login(username=user.username, password=PASSWORD):
            self.fail('User login failed!')

        return user

    def assertRedirectsToLogin(self, response):
        # Note: Not using assertRedirects because I don't want to deal with creating a login template
        self.assertEqual(302, response.status_code)
        url = urllib.parse.urlparse(response.url)
        self.assertEqual(settings.LOGIN_URL, url[2])

    def test_logged_out(self):
        response = self.client.get(reverse('tos_accept'))
        self.assertRedirectsToLogin(response)

        response = self.client.post(reverse('tos_accept'))
        self.assertRedirectsToLogin(response)

    def test_no_agreement(self):
        self.get_and_login_user()
        self.assertRaises(Agreement.DoesNotExist, self.client.get, reverse('tos_accept'))
        self.assertRaises(Agreement.DoesNotExist, self.client.post, reverse('tos_accept'))

    def test_no_agreement_version(self):
        Agreement.objects.create(name=TOS_NAME)
        self.get_and_login_user()
        self.assertRaises(NoVersionException, self.client.get, reverse('tos_accept'))
        self.assertRaises(NoVersionException, self.client.post, reverse('tos_accept'))

    def test_post_valid_agreement(self):
        agreement = Agreement.objects.create(name=TOS_NAME)
        get_agreement_version(agreement)
        self.get_and_login_user()

        next = '/'
        response = self.client.post(reverse('tos_accept'))
        self.assertEqual(302, response.status_code)
        url = urllib.parse.urlparse(response.url)
        self.assertEqual(next, url[2])

        next = '/abc123'
        response = self.client.post(reverse('tos_accept'), {'next': next})
        self.assertEqual(302, response.status_code)
        url = urllib.parse.urlparse(response.url)
        self.assertEqual(next, url[2])

    def test_get_valid_agreement(self):
        agreement = Agreement.objects.create(name=TOS_NAME)
        get_agreement_version(agreement)
        self.get_and_login_user()

        response = self.client.get(reverse('tos_accept'))
        self.assertEqual(200, response.status_code)


class TermsOfServiceAcceptanceMiddlewareTests(TestCase):
    def setUp(self):
        self.middleware = TermsOfServiceAcceptanceMiddleware()
        self.user = get_user()
        self.agreement = Agreement.objects.create(name=TOS_NAME)
        get_agreement_version(self.agreement)

    def test_process_request_accepted(self):
        self.agreement.accept(self.user)

        if not self.client.login(username=self.user.username, password=PASSWORD):
            self.fail('User login failed!')

        request = RequestFactory().get('/')
        request.user = self.user
        response = self.middleware.process_request(request)

        self.assertIsNone(response)

    def test_process_request_unaccepted(self):
        if not self.client.login(username=self.user.username, password=PASSWORD):
            self.fail('User login failed!')

        request = RequestFactory().get('/?param=xxx')
        request.user = self.user
        response = self.middleware.process_request(request)

        self.assertIs(type(response), HttpResponseRedirect)

        next_param = urllib.parse.urlencode({'next': '/?%s' % urllib.parse.urlencode({'param': 'xxx'})})
        expected_url = reverse('tos_accept') + '?%s' % next_param
        self.assertEqual(expected_url, response.url)

    def test_ignored_urls(self):
        if not self.client.login(username=self.user.username, password=PASSWORD):
            self.fail('User login failed!')

        ignored_paths = [reverse('tos_accept'), resolve_url(settings.LOGIN_URL), resolve_url(settings.LOGOUT_URL),
                        reverse('tos'), reverse('privacy_policy')]

        for path in ignored_paths:
            request = RequestFactory().get(path)
            request.user = self.user
            self.assertIsNone(self.middleware.process_request(request), 'The path %s should be ignored!' % path)


class TermsOfServiceViewTests(TestCase):
    def test_page_loads(self):
        agreement = Agreement.objects.create(name=TOS_NAME)
        get_agreement_version(agreement)

        response = self.client.get(reverse('tos'))
        self.assertEqual(200, response.status_code)


class PrivacyPolicyViewTests(TestCase):
    def test_page_loads(self):
        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(200, response.status_code)
