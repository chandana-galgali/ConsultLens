from django.urls import path

from . import views

urlpatterns = [
    # Final URL (if Care mounts plugins at /api/<name>/):  /api/care_consultlens/v1/proxy/<subpath>
    path("v1/proxy/<path:subpath>", views.proxy, name="consultlens-proxy"),
]
