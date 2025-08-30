from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config import settings

urlpatterns = [
    path("", include("apps.pages.urls")),
    path("admin/", admin.site.urls),
    path("reservation/", include("apps.reservations.urls")),
]

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("rosetta/", include("rosetta.urls")),
    ]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    ]
