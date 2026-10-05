import json
from collections import defaultdict
from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import APIKey, Buyer, Cart, Customer, Order, Product, Seller


def is_seller_user(user):
    return user.is_authenticated and hasattr(user, "seller_profile")


def is_buyer_user(user):
    return user.is_authenticated and hasattr(user, "buyer_profile")


def get_seller_for_user(user):
    return Seller.objects.filter(user=user).first()


def get_buyer_for_user(user):
    return Buyer.objects.filter(user=user).first()


def seller_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('seller_login')}?next={request.get_full_path()}")

        if not is_seller_user(request.user):
            messages.error(request, "Please sign in with a seller account to access the seller dashboard.")
            return redirect("seller_login")

        return view_func(request, *args, **kwargs)

    return wrapper


def buyer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('buyer_login')}?next={request.get_full_path()}")

        if not is_buyer_user(request.user):
            messages.error(request, "Please sign in with a buyer account to continue shopping.")
            return redirect("buyer_login")

        return view_func(request, *args, **kwargs)

    return wrapper


def build_analytics_payload(seller):
    orders = Order.objects.all()#filter(seller=seller)
    products = Product.objects.all() #filter(seller=seller)
    customers = Customer.objects.all() #filter(seller=seller)
    total_sales = orders.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

    return {
        "seller": seller.user.username,
        "total_sales": float(total_sales),
        "total_orders": orders.count(),
        "total_products": products.count(),
        "total_customers": customers.count(),
    }


def build_storefront_context(request, extra_context=None):
    context = {
        "cart_items": [],
        "cart_count": 0,
        "cart_total": Decimal("0.00"),
        "is_buyer": is_buyer_user(request.user),
        "is_seller": is_seller_user(request.user),
    }

    if is_buyer_user(request.user):
        cart_items = list(Cart.objects.filter(user=request.user).select_related("product"))
        cart_total = Decimal("0.00")

        for item in cart_items:
            subtotal = Decimal(str(item.product.price)) * item.quantity
            item.subtotal = subtotal
            cart_total += subtotal

        context.update(
            {
                "cart_items": cart_items[:4],
                "cart_count": sum(item.quantity for item in cart_items),
                "cart_total": cart_total,
            }
        )

    if extra_context:
        context.update(extra_context)

    return context


def build_monthly_sales_series(seller):
    monthly_sales = (
        Order.objects.filter(seller=seller)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )

    labels = []
    values = []
    for entry in monthly_sales:
        if entry["month"] is None:
            continue
        labels.append(entry["month"].strftime("%b %Y"))
        values.append(float(entry["total"] or 0))

    return labels, values


def index(request):
    return render(request, "index.html", build_storefront_context(request))


def home2(request):
    return render(request, "home-02.html", build_storefront_context(request))


def home3(request):
    return render(request, "home-03.html", build_storefront_context(request))


def productdetails(request):
    return render(request, "product-detail.html", build_storefront_context(request))


def about(request):
    return render(request, "about.html", build_storefront_context(request))


def tips(request):
    return render(request, "tips.html", build_storefront_context(request))


def seller_index(request):
    return redirect("seller_dashboard" if is_seller_user(request.user) else "seller_login")


@require_http_methods(["GET", "POST"])
def buyer_signup_view(request):
    if is_buyer_user(request.user):
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not username or not email or not password:
            return render(request, "buyer_signup.html", {"error": "All fields are required."})

        if User.objects.filter(username=username).exists():
            return render(request, "buyer_signup.html", {"error": "Username already exists."})

        user = User.objects.create_user(username=username, email=email, password=password)
        Buyer.objects.create(user=user)
        messages.success(request, "Your buyer account is ready. Please sign in to continue shopping.")
        return redirect("buyer_login")

    return render(request, "buyer_signup.html")


@require_http_methods(["GET", "POST"])
def buyer_login_view(request):
    if is_buyer_user(request.user):
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "buyer_login.html", {"error": "Invalid username or password."})

        if not Buyer.objects.filter(user=user).exists():
            return render(
                request,
                "buyer_login.html",
                {"error": "This account is not a buyer account. Please use the seller login portal."},
            )

        login(request, user)
        messages.success(request, "Welcome back to the ecommerce store.")
        next_url = request.GET.get("next")
        return redirect(next_url or "home")

    return render(request, "buyer_login.html")


def buyer_logout_view(request):
    logout(request)
    return redirect("buyer_login")


@require_http_methods(["GET", "POST"])
def seller_signup_view(request):
    if is_seller_user(request.user):
        return redirect("seller_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not username or not email or not password:
            return render(request, "signup.html", {"error": "All fields are required."})

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already exists."})

        user = User.objects.create_user(username=username, email=email, password=password)
        Seller.objects.create(user=user)
        messages.success(request, "Your seller account is ready. Please sign in to access your dashboard.")
        return redirect("seller_login")

    return render(request, "signup.html")


@require_http_methods(["GET", "POST"])
def seller_login_view(request):
    if is_seller_user(request.user):
        return redirect("seller_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "login.html", {"error": "Invalid username or password."})

        if not Seller.objects.filter(user=user).exists():
            return render(
                request,
                "login.html",
                {"error": "This account is not a seller account. Please use the buyer login portal."},
            )

        login(request, user)
        messages.success(request, "Welcome back to your seller dashboard.")
        next_url = request.GET.get("next")
        return redirect(next_url or "seller_dashboard")

    return render(request, "login.html")


def seller_logout_view(request):
    logout(request)
    return redirect("seller_login")


@seller_required
def dashboard_view(request):
    seller = get_seller_for_user(request.user)
    analytics = build_analytics_payload(seller)
    chart_labels, chart_values = build_monthly_sales_series(seller)

    context = {
        "analytics": analytics,
        "api_key": APIKey.objects.filter(seller=seller).first(),
        "top_products": Product.objects.all().order_by("-price", "name")[:5],
        "recent_orders": Order.objects.all().order_by("-created_at")[:5],
        "chart_labels": json.dumps(chart_labels),
        "chart_values": json.dumps(chart_values),
    }
    return render(request, "dashboard.html", context)


@seller_required
@require_POST
def generate_api_key_view(request):
    seller = get_seller_for_user(request.user)
    api_key, created = APIKey.objects.get_or_create(seller=seller)

    if created:
        messages.success(request, "API key generated successfully.")
    else:
        api_key.regenerate_key()
        messages.success(request, "API key regenerated successfully.")

    return redirect("seller_dashboard")


@require_GET
def analytics_api_view(request):
    auth_header = request.headers.get("Authorization", "")
    prefix = "Api-Key "

    if not auth_header.startswith(prefix):
        return JsonResponse({"detail": "Invalid API key."}, status=403)

    key = auth_header[len(prefix):].strip()

    try:
        api_key = APIKey.objects.select_related("seller__user").get(key=key)
    except APIKey.DoesNotExist:
        return JsonResponse({"detail": "Invalid API key."}, status=403)

    return JsonResponse(build_analytics_payload(api_key.seller))


def product_list(request):
    products = Product.objects.select_related("seller").all().order_by("name")
    return render(request, "products.html", build_storefront_context(request, {"products": products}))


def recommend_products(request, product_id):
    target = get_object_or_404(Product, id=product_id)
    recommended_products = (
        Product.objects.exclude(id=target.id).filter(category=target.category).order_by("-price")[:4]
    )

    if not recommended_products:
        recommended_products = Product.objects.exclude(id=target.id).order_by("-price")[:4]

    click_counts = request.session.get("click_counts", {})
    click_counts[str(product_id)] = click_counts.get(str(product_id), 0) + 1
    request.session["click_counts"] = click_counts

    return render(
        request,
        "recommendation.html",
        build_storefront_context(
            request,
            {
                "target": target,
                "recommended_products": recommended_products,
            },
        ),
    )


def user_liked(request):
    click_counts = request.session.get("click_counts", {})
    sorted_clicks = sorted(click_counts.items(), key=lambda item: item[1], reverse=True)

    liked_products = []
    for product_id, count in sorted_clicks:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        product.click_count = count
        liked_products.append(product)

    return render(request, "user_liked.html", build_storefront_context(request, {"liked_products": liked_products}))


@buyer_required
def add_to_cart(request, product_id):
    if Product.objects.filter(id=product_id).exists():
        product = Product.objects.get(id=product_id)
    else:
        product, _ = Product.objects.get_or_create(
            name=request.POST.get("name", "Search Result Item"),
            price=float(request.POST.get("price", 0)),
            defaults={
                "category": "search",
                "brand": "Unknown",
                "condition": "New",
                "sustainability_score": 80,
                "ethical_score": 80,
                "image_url": request.POST.get("image"),
            },
        )

    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save(update_fields=["quantity"])

    messages.success(request, f"{product.name} has been added to your cart.")
    return redirect("view_cart")


@buyer_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user).select_related("product")
    total = Decimal("0.00")

    for item in cart_items:
        item.subtotal = Decimal(str(item.product.price)) * item.quantity
        total += item.subtotal

    return render(
        request,
        "cart.html",
        build_storefront_context(request, {"cart_items": cart_items, "total": total}),
    )


@buyer_required
def remove_from_cart(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)
    item.delete()
    messages.success(request, "Item removed from your cart.")
    return redirect("view_cart")


@buyer_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).select_related("product")
    if not cart_items.exists():
        return redirect("view_cart")

    total = Decimal("0.00")
    for item in cart_items:
        item.subtotal = Decimal(str(item.product.price)) * item.quantity
        total += item.subtotal

    return render(
        request,
        "checkout.html",
        build_storefront_context(request, {"cart_items": cart_items, "total": total, "qr_code": None}),
    )


def search_products(request):
    query = request.GET.get("query", "").strip()
    products = Product.objects.none()

    if query:
        products = Product.objects.filter(name__icontains=query).order_by("name")
        if not products.exists():
            products = Product.objects.filter(category__icontains=query).order_by("name")
        if not products.exists():
            products = Product.objects.filter(brand__icontains=query).order_by("name")

    return render(
        request,
        "search_results.html",
        build_storefront_context(request, {"products": products, "query": query}),
    )


def view_similar(request, category):
    products = Product.objects.filter(category__iexact=category).order_by("name")
    return render(
        request,
        "search_results.html",
        build_storefront_context(request, {"products": products, "query": category}),
    )


@buyer_required
def place_order(request):
    if request.method != "POST":
        return redirect("checkout")

    cart_items = Cart.objects.filter(user=request.user).select_related("product__seller")
    if not cart_items.exists():
        return redirect("view_cart")

    seller_totals = defaultdict(Decimal)
    grand_total = Decimal("0.00")
    customer_name = request.user.get_full_name().strip() or request.user.username

    for item in cart_items:
        subtotal = Decimal(str(item.product.price)) * item.quantity
        grand_total += subtotal
        if item.product.seller:
            seller_totals[item.product.seller] += subtotal

    for seller, total in seller_totals.items():
        Order.objects.create(seller=seller, total_amount=total)
        Customer.objects.get_or_create(seller=seller, name=customer_name)

    cart_items.delete()
    messages.success(
        request,
        "Order placed successfully. Seller dashboards and API analytics now include this purchase.",
    )
    return render(request, "place_order.html", build_storefront_context(request, {"total": grand_total}))


@buyer_required
def checkout_single(request, cart_id):
    item = get_object_or_404(Cart.objects.select_related("product"), id=cart_id, user=request.user)
    item.subtotal = Decimal(str(item.product.price)) * item.quantity

    return render(
        request,
        "checkout.html",
        build_storefront_context(request, {"cart_items": [item], "total": item.subtotal, "qr_code": None}),
    )
