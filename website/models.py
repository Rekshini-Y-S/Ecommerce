import secrets

from django.contrib.auth.models import User
from django.db import models


class Seller(models.Model):
    # Each seller is backed by Django's built-in user account.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Buyer(models.Model):
    # Buyers use separate storefront login/signup routes from sellers.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="buyer_profile")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class APIKey(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name="api_key")
    key = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def generate_unique_key():
        while True:
            candidate = secrets.token_hex(20)
            if not APIKey.objects.filter(key=candidate).exists():
                return candidate

    def regenerate_key(self):
        self.key = self.generate_unique_key()
        self.save(update_fields=["key", "updated_at"])

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_unique_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"API key for {self.seller.user.username}"


class Product(models.Model):
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name="products",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.FloatField()
    condition = models.CharField(max_length=50)
    sustainability_score = models.IntegerField()
    ethical_score = models.IntegerField()
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ImageField(upload_to="product_images/", blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def image(self):
        # Prefer uploaded media first, then an external URL, then a small fallback.
        if self.image_file:
            return self.image_file.url
        if self.image_url:
            return self.image_url
        return "/static/default.jpg"


class Order(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.seller.user.username}"


class Customer(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="customers")
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("seller", "name")

    def __str__(self):
        return f"{self.name} ({self.seller.user.username})"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
