from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="home"),
    path("signup/", views.buyer_signup_view, name="buyer_signup"),
    path("login/", views.buyer_login_view, name="buyer_login"),
    path("logout/", views.buyer_logout_view, name="buyer_logout"),
    path("home2/", views.home2, name="home2"),
    path("home3/", views.home3, name="home3"),
    path("details/", views.productdetails, name="details"),
    path("about/", views.about, name="about"),
    path("tips/", views.tips, name="tips"),
    path("products/", views.product_list, name="product_list"),
    path("recommend/<int:product_id>/", views.recommend_products, name="recommend_products"),
    path("liked/", views.user_liked, name="user_liked"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path("remove-from-cart/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout-single/<int:cart_id>/", views.checkout_single, name="checkout_single"),
    path("place-order/", views.place_order, name="place_order"),
    path("search/", views.search_products, name="search"),
    path("view-similar/<str:category>/", views.view_similar, name="view_similar"),
]
