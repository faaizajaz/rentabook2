from django.shortcuts import redirect, render

from .forms import UserRegistrationForm


# Create your views here.
def RegisterUser(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "user/register.html", {"form": form})
