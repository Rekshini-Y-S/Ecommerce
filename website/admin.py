from django.contrib import admin

from .models import APIKey, Buyer, Cart, Customer, Order, Product, Seller


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username", "user__email")


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username", "user__email")


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("seller", "key", "created_at", "updated_at")
    search_fields = ("seller__user__username", "key")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "seller", "category", "brand", "price")
    list_filter = ("category", "brand")
    search_fields = ("name", "seller__user__username")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "seller", "total_amount", "created_at")
    list_filter = ("created_at",)
    search_fields = ("seller__user__username",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "seller", "created_at")
    search_fields = ("name", "seller__user__username")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity")
