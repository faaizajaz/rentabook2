from django.shortcuts import redirect, render

from .forms import UserRegistrationForm


# Create your views here.
def RegisterUser(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "user/regcomplete.html", {"nodata": "nodata"})
    else:
        form = UserRegistrationForm()
    return render(request, "user/register.html", {"form": form})
