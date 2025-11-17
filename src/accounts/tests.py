from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from accounts.models import UserProfile


class RegistrationTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_register_creates_user_and_profile(self):
		data = {
			"register-fullname": "Jane Doe",
			"register-role": "buyer",
			"register-email": "jane@example.com",
			"register-password": "Strong123",
			"register-confirm-password": "Strong123",
		}
		resp = self.client.post(reverse("register_user"), data, follow=True)
		self.assertEqual(resp.status_code, 200)

		user = User.objects.get(email="jane@example.com")
		profile = UserProfile.objects.get(user=user)
		self.assertEqual(profile.role, "buyer")
		self.assertEqual(user.first_name, "Jane")
		self.assertEqual(user.last_name, "Doe")

	def test_register_duplicate_email_rejected(self):
		User.objects.create_user(
			username="existing",
			email="dup@example.com",
			password="Strong123",
		)
		data = {
			"register-fullname": "Dup User",
			"register-role": "buyer",
			"register-email": "dup@example.com",
			"register-password": "Strong123",
			"register-confirm-password": "Strong123",
		}
		resp = self.client.post(reverse("register_user"), data, follow=True)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(User.objects.filter(email="dup@example.com").count(), 1)

	def test_register_missing_role_rejected(self):
		data = {
			"register-fullname": "No Role",
			"register-role": "",
			"register-email": "norole@example.com",
			"register-password": "Strong123",
			"register-confirm-password": "Strong123",
		}
		resp = self.client.post(reverse("register_user"), data, follow=True)
		self.assertEqual(resp.status_code, 200)
		self.assertFalse(User.objects.filter(email="norole@example.com").exists())

	def test_register_get_redirects_to_login_register(self):
		resp = self.client.get(reverse("register_user"))
		self.assertEqual(resp.status_code, 302)
		self.assertEqual(resp["Location"], reverse("login_register"))


class LoginFlowTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(
			username="john",
			email="john@example.com",
			password="Strong123",
		)
		UserProfile.objects.create(user=self.user, role="buyer")

	def test_login_success_sets_session(self):
		resp = self.client.post(
			reverse("login_user"),
			{"login-email": "john@example.com", "login-password": "Strong123"},
		)
		self.assertEqual(resp.status_code, 302)
		self.assertEqual(resp["Location"], reverse("home"))

		resp2 = self.client.get(reverse("buyer_profile"))
		self.assertEqual(resp2.status_code, 200)

	def test_login_wrong_password_stays_anonymous(self):
		resp = self.client.post(
			reverse("login_user"),
			{"login-email": "john@example.com", "login-password": "wrong"},
			follow=True,
		)
		self.assertEqual(resp.status_code, 200)

		resp2 = self.client.get(reverse("buyer_profile"))
		self.assertEqual(resp2.status_code, 302)

	def test_logout_protects_views_again(self):
		self.client.login(username="john", password="Strong123")
		resp = self.client.get(reverse("buyer_profile"))
		self.assertEqual(resp.status_code, 200)

		resp = self.client.get(reverse("logout_user"))
		self.assertEqual(resp.status_code, 302)

		resp2 = self.client.get(reverse("buyer_profile"))
		self.assertEqual(resp2.status_code, 302)


class PortalAccessTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(
			username="buyer",
			email="buyer@example.com",
			password="Strong123",
		)
		UserProfile.objects.create(user=self.user, role="buyer")

	def test_anonymous_redirected_from_protected_pages(self):
		protected = [
			"buyer_profile",
			"order_history",
			"invoice_page",
			"artisan_dashboard",
			"create_listing",
			"edit_listing",
			"fulfillment",
			"inventory_manager",
			"reports_page",
		]
		for name in protected:
			if name in ["invoice_page", "edit_listing"]:
				resp = self.client.get(reverse(name, args=[1]))
			else:
				resp = self.client.get(reverse(name))
			self.assertEqual(resp.status_code, 302, msg=f"{name} should redirect for anonymous")

	def test_authenticated_user_can_access_portal_pages(self):
		self.client.login(username="buyer", password="Strong123")
		urls = [
			("buyer_profile", []),
			("order_history", []),
			("invoice_page", [1]),
			("artisan_dashboard", []),
			("create_listing", []),
			("edit_listing", [1]),
			("fulfillment", []),
			("inventory_manager", []),
			("reports_page", []),
		]
		for name, args in urls:
			resp = self.client.get(reverse(name, args=args))
			self.assertEqual(resp.status_code, 200, msg=f"{name} should be accessible when logged in")
