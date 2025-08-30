from django.contrib.auth.decorators import login_not_required  # type: ignore
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View


@method_decorator(decorator=login_not_required, name="dispatch")
class HomeView(View):
    template_name = "pages/home.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {}
        # del request.session["reservation_data"]
        print()
        print(request.session.get("reservation_data"))
        # print(request.session.delete("reservation_data"))
        print()
        return render(request, self.template_name, context)
