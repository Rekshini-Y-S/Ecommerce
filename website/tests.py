from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import APIKey, Buyer, Cart, Customer, Order, Product, Seller


class EcommerceAuthAndAnalyticsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.seller_user = User.objects.create_user(
            username="sellerone",
            email="seller1@example.com",
            password="StrongPass123",
        )
        self.seller = Seller.objects.create(user=self.seller_user)

        self.other_seller_user = User.objects.create_user(
            username="sellertwo",
            email="seller2@example.com",
            password="StrongPass123",
        )
        self.other_seller = Seller.objects.create(user=self.other_seller_user)

        self.buyer_user = User.objects.create_user(
            username="buyerone",
            email="buyer1@example.com",
            password="StrongPass123",
        )
        self.buyer = Buyer.objects.create(user=self.buyer_user)

        self.product = Product.objects.create(
            seller=self.seller,
            name="Winter Jacket",
            category="Outerwear",
            brand="Northwind",
            price=Decimal("2499.00"),
            condition="New",
            sustainability_score=88,
            ethical_score=91,
        )
        Product.objects.create(
            seller=self.other_seller,
            name="Other Seller Product",
            category="Accessories",
            brand="Elsewhere",
            price=Decimal("999.00"),
            condition="New",
            sustainability_score=75,
            ethical_score=76,
        )

        Order.objects.create(seller=self.seller, total_amount=Decimal("1500.00"))
        Customer.objects.create(seller=self.seller, name="Asha")
        self.api_key = APIKey.objects.create(seller=self.seller)

    def test_storefront_home_is_public(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_buyer_signup_creates_buyer_account(self):
        response = self.client.post(
            reverse("buyer_signup"),
            {
                "username": "newbuyer",
                "email": "newbuyer@example.com",
                "password": "AnotherPass123",
            },
        )

        self.assertRedirects(response, reverse("buyer_login"))
        self.assertTrue(Buyer.objects.filter(user__username="newbuyer").exists())
        self.assertFalse(Seller.objects.filter(user__username="newbuyer").exists())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_buyer_login_redirects_to_home(self):
        response = self.client.post(
            reverse("buyer_login"),
            {
                "username": "buyerone",
                "password": "StrongPass123",
            },
        )

        self.assertRedirects(response, reverse("home"))

    def test_seller_signup_creates_seller_account(self):
        response = self.client.post(
            reverse("seller_signup"),
            {
                "username": "newmerchant",
                "email": "newmerchant@example.com",
                "password": "AnotherPass123",
            },
        )

        self.assertRedirects(response, reverse("seller_login"))
        self.assertTrue(Seller.objects.filter(user__username="newmerchant").exists())
        self.assertFalse(Buyer.objects.filter(user__username="newmerchant").exists())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_buyer_login_rejects_seller_account(self):
        response = self.client.post(
            reverse("buyer_login"),
            {
                "username": "sellerone",
                "password": "StrongPass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not a buyer account")

    def test_seller_login_rejects_buyer_account(self):
        response = self.client.post(
            reverse("seller_login"),
            {
                "username": "buyerone",
                "password": "StrongPass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not a seller account")

    def test_seller_dashboard_requires_seller_login(self):
        response = self.client.get(reverse("seller_dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("seller_login"), response.url)

    def test_buyer_checkout_updates_seller_dashboard_metrics_and_api(self):
        self.client.login(username="buyerone", password="StrongPass123")
        Cart.objects.create(user=self.buyer_user, product=self.product, quantity=2)

        response = self.client.post(reverse("place_order"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.filter(seller=self.seller).count(), 2)
        self.assertTrue(Customer.objects.filter(seller=self.seller, name="buyerone").exists())

        dashboard_client = Client()
        dashboard_client.login(username="sellerone", password="StrongPass123")
        dashboard_response = dashboard_client.get(reverse("seller_dashboard"))

        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(dashboard_response.context["analytics"]["total_orders"], 2)
        self.assertEqual(dashboard_response.context["analytics"]["total_customers"], 2)
        self.assertEqual(dashboard_response.context["analytics"]["total_products"], 1)
        self.assertEqual(dashboard_response.context["analytics"]["total_sales"], 6498.0)

        api_response = self.client.get(
            reverse("seller_analytics_api"),
            HTTP_AUTHORIZATION=f"Api-Key {self.api_key.key}",
        )

        self.assertEqual(api_response.status_code, 200)
        self.assertJSONEqual(
            api_response.content,
            {
                "seller": "sellerone",
                "total_sales": 6498.0,
                "total_orders": 2,
                "total_products": 1,
                "total_customers": 2,
            },
        )

    def test_analytics_api_returns_403_for_invalid_key(self):
        response = self.client.get(
            reverse("seller_analytics_api"),
            HTTP_AUTHORIZATION="Api-Key invalid-key",
        )

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {"detail": "Invalid API key."})
