from bookquery.forms import BookQueryForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def BookQueryView(request, **kwargs):
    if request.method == "POST":
        form = BookQueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.user = request.user
            query.save()

            if query.search_type == "Fiction":
                num_pages = query.get_num_pages_fiction()
            else:
                num_pages = query.get_num_pages_non_fiction()

            print(num_pages)
            print(query.search_type)

            # Here we need to figure out how many pages are there.
            # query.get

    else:
        form = BookQueryForm()

    return render(request, "bookquery/search.html", {"form": form})
