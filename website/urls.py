from django.urls import include, path


urlpatterns = [
    path("seller/", include("website.seller_urls")),
    path("", include("website.store_urls")),
]
