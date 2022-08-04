from bookquery.forms import BookQueryForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def BookQueryView(request, **kwargs):
    if request.method == "POST":
        form = BookQueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=True)
            query.user = request.user
            print("You did a search")
            query.save()

    else:
        form = BookQueryForm()

    return render(request, "bookquery/search.html", {"form": form})
