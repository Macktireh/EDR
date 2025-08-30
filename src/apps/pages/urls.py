from django.urls import path

from apps.pages.views import HomeView

app_name = "pages"

urlpatterns = [
    path(route="", view=HomeView.as_view(), name="home"),
]
