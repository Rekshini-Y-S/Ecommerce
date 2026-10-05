from django.urls import path
from . import views

urlpatterns = [
    path("", views.seller_index, name="seller_home"),
    path("signup/", views.seller_signup_view, name="seller_signup"),
    path("login/", views.seller_login_view, name="seller_login"),
    path("logout/", views.seller_logout_view, name="seller_logout"),
    path("dashboard/", views.dashboard_view, name="seller_dashboard"),
    path("generate-key/", views.generate_api_key_view, name="seller_generate_api_key"),
    path("api/analytics/", views.analytics_api_view, name="seller_analytics_api"),
]
