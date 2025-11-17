from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from unittest.mock import patch
from django.http import HttpResponse

from accounts.middleware import LoginRequiredMiddleware
from accounts.models import UserProfile

class LoginRequiredMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="mw", password="pass123")
        UserProfile.objects.create(user=self.user, role="buyer")
        self.ok = HttpResponse("OK")

    def _mw(self):
        return LoginRequiredMiddleware(lambda r: self.ok)

    def test_exact_public_path(self):
        req = self.factory.get("/")
        req.user = AnonymousUser()
        resp = self._mw()(req)
        self.assertEqual(resp.status_code, 200)

    def test_prefix_public_path(self):
        req = self.factory.get("/static/css/site.css")
        req.user = AnonymousUser()
        resp = self._mw()(req)
        self.assertEqual(resp.status_code, 200)

    def test_authenticated_access(self):
        req = self.factory.get("/profile/")
        req.user = self.user
        resp = self._mw()(req)
        self.assertEqual(resp.status_code, 200)

    def test_redirect_anonymous_protected(self):
        req = self.factory.get("/profile/")
        req.user = AnonymousUser()
        resp = self._mw()(req)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login_register"), resp["Location"])

    def test_public_via_view_name(self):
        class Match: url_name = 'home'
        with patch("accounts.middleware.resolve", return_value=Match()):
            req = self.factory.get("/some/alias/")
            req.user = AnonymousUser()
            resp = self._mw()(req)
            self.assertEqual(resp.status_code, 200)

    def test_resolver404_non_public(self):
        from django.urls import Resolver404
        with patch("accounts.middleware.resolve", side_effect=Resolver404):
            req = self.factory.get("/ghost/")
            req.user = AnonymousUser()
            resp = self._mw()(req)
            self.assertEqual(resp.status_code, 302)

class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_success(self):
        data = {
            'register-fullname': 'Alice Smith',
            'register-role': 'buyer',
            'register-email': 'alice@example.com',
            'register-password': 'Strong123',
            'register-confirm-password': 'Strong123',
        }
        resp = self.client.post(reverse('register_user'), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(email='alice@example.com').exists())

    def test_register_password_mismatch(self):
        data = {
            'register-fullname': 'Bob',
            'register-role': 'buyer',
            'register-email': 'bob@example.com',
            'register-password': 'a',
            'register-confirm-password': 'b',
        }
        resp = self.client.post(reverse('register_user'), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email='bob@example.com').exists())

    def test_login_email_not_found(self):
        data = {'login-email': 'none@example.com', 'login-password': 'x'}
        resp = self.client.post(reverse('login_user'), data, follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_login_success_and_logout(self):
        u = User.objects.create_user(username='carl', email='carl@example.com', password='Pass12345')
        data = {'login-email': 'carl@example.com', 'login-password': 'Pass12345'}
        resp = self.client.post(reverse('login_user'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], reverse('home'))
        self.client.force_login(u)
        resp = self.client.get(reverse('logout_user'))
        self.assertEqual(resp.status_code, 302)

class SimpleRenderViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_public_pages_render(self):
        names = [
            'home', 'shopping_cart', 'product_details', 'login_register'
        ]
        for name in names:
            if name == 'product_details':
                resp = self.client.get(reverse(name, args=[1]))
            else:
                resp = self.client.get(reverse(name))
            # Only the home and login/register pages are public for anonymous users;
            # other views (including product details) are protected by the middleware.
            if name in ['home', 'login_register']:
                self.assertEqual(resp.status_code, 200)
            else:
                self.assertEqual(resp.status_code, 302)
