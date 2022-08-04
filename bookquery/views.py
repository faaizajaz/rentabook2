import json

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

            ########## FICTION #############
            if query.search_type == "Fiction":
                num_pages = query.get_num_pages_fiction()
                results = []

                # HANDLE FICTION SEARCH AND RETRIEVAL HERE

            #################### NON-FICTION ##################
            else:
                num_pages = query.get_num_pages_non_fiction()
                results = query.search_non_fiction(num_pages)

                if len(results) == 0:
                    print("## RENTABOOK ##: No mobi or epub found on Libgren")
                else:
                    if results[0] == "timeout":
                        print("## RENTABOOK ##: Search timed out.")
                    else:
                        print("## RENTABOOK ##: Mobi/epub results found on Libgen")

                json_results = json.dumps(results)
                request.session["search_results"] = results

                if len(results) > 0:
                    if results[0] == "timeout":
                        print("## RENTABOOK ##: Redirecting to search timeout page")
                        return render(
                            request, "bookquery/timeout.html", {"nodata": "nodata"}
                        )
                    else:
                        print("## RENTABOOK ##: Redirecting to results page")

                        return render(
                            request,
                            "bookquery/results.html",
                            {"results": results, "json_results": json_results},
                        )
                else:
                    print("## RENTABOOK ##: Redirecting to no results page")
                    return render(
                        request, "bookquery/noresults.html", {"nodata": "nodata"}
                    )
            ####################################################

    else:
        form = BookQueryForm()

    return render(request, "bookquery/search.html", {"form": form})
