import json
import os
import urllib.request

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from rentabook2 import settings
from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import BookQueryForm


@login_required
def BookQueryView(request, **kwargs):
    if request.method == "POST":
        form = BookQueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.user = request.user
            query.save()
            print("## RENTABOOK ##: Search beginning.")

            ########## FICTION #############
            if query.search_type == "Fiction":
                try:
                    num_pages = query.get_num_pages_fiction()
                    results = query.search_fiction(num_pages)
                    # print(results)

                    if len(results) == 0:
                        print("## RENTABOOK ##: No mobi or epub found on Libgen")
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
                                {
                                    "results": results,
                                    "json_results": json_results,
                                    "user": query.user.username,
                                },
                            )
                    else:
                        print("## RENTABOOK ##: Redirecting to no results page")
                        return render(
                            request, "bookquery/noresults.html", {"nodata": "nodata"}
                        )
                except:
                    print("## RENTABOOK ##: No mobi or epub found on Libgen")
                    return render(
                        request, "bookquery/noresults.html", {"nodata": "nodata"}
                    )

            #################### NON-FICTION ##################
            else:
                num_pages = query.get_num_pages_non_fiction()
                results = query.search_non_fiction(num_pages)

                if len(results) == 0:
                    print("## RENTABOOK ##: No mobi or epub found on Libgen")
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
                            {
                                "results": results,
                                "json_results": json_results,
                                "user": query.user.username,
                            },
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


class DownloadView(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, book_id=None):
        match_book = self.get_match_book(request, book_id)
        match_book_title = match_book["Title"]

        try:
            print("## RENTABOOK ##: Trying to get download link")
            download_link = self.get_download_link(match_book)
            print("## RENTABOOK ##: SUCCESS - Got download link")

        except:
            print("## RENTABOOK ##: ERROR - Failed getting download link")
            return JsonResponse(
                {
                    "detail": (
                        "Couldn't find a download link. Try selecting a different file"
                    ),
                    "error": "error",
                }
            )

        try:
            print("## RENTABOOK ##: Tring to download book")
            downloaded_file = self.download_book(match_book, download_link)
            print("## RENTABOOK ##: SUCCESS - Downloaded book.")
        except:
            print("## RENTABOOK ##: ERROR - Failed to download file")
            return JsonResponse(
                {
                    "detail": (
                        "Couldn't download the file for some reason. Try selecting a"
                        " different file."
                    ),
                    "error": "error",
                }
            )

        try:
            print("## RENTABOOK ##: Tring to email book")
            self.email_book(request, match_book, downloaded_file)
            print("## RENTABOOK ##: SUCCESS - Emailed book")
        except:
            print("## RENTABOOK ##: ERROR - Failed to email the book")
            return JsonResponse(
                {
                    "detail": (
                        "Error emailing the book. Try again and if issue persists, tell"
                        " Faaiz"
                    ),
                    "error": "error",
                }
            )

        print("## RENTABOOK ##: SUCCESS - Transaction complete!")
        return JsonResponse(
            {
                "detail": (
                    f"Book was successfully downloaded!"
                    " Wait 5 minutes for the book to appear on your Kindle."
                )
            }
        )

    def get_match_book(self, request, book_id):
        if request.session["search_results"]:
            for book in request.session["search_results"]:
                if book["ID"] == book_id:
                    request.session["match_book"] = book
                    return book
            return
        else:
            print("Didn't find a match book.")
            return

    def get_download_link(self, match_book):
        mirror_url = match_book["Mirror_1"]

        print("# get_download_link #: Downloading page")
        with urllib.request.urlopen(mirror_url) as download_page:
            download_page_html = download_page.read()

        soup = BeautifulSoup(download_page_html, "html.parser")

        print("# get_download_link #: Getting download link")
        download_link = soup.h2.a.get("href")

        print("# get_download_link #: SUCCESS - Got the download link")

        return download_link

    def download_book(self, match_book, download_link):
        file_title = f"{match_book['Title']}.epub"
        print(download_link)
        print("# download_book #: Downloading book")
        r = requests.get(download_link, allow_redirects=True)
        print("# download_book #: Saving book to file")
        with open(os.path.join(settings.MEDIA_ROOT, file_title), "wb") as f:
            f.write(r.content)

        print("# download_book #: SUCCESS - Saved book to file complete")

        downloaded_file = os.path.join(settings.MEDIA_ROOT, file_title)

        return downloaded_file

    def email_book(self, request, match_book, downloaded_file):

        subject = f"Emailing: {match_book['Title']}"
        body = ""
        from_email = settings.EMAIL_HOST_USER
        to = (request.user.email,)

        email = EmailMessage(subject=subject, body=body, from_email=from_email, to=to)
        print("# email_book #: Attaching file")
        email.attach_file(downloaded_file)
        email.send()
        print("# email_book #: SUCCESS - Email sent.")

        return


class DownloadLocalView(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, book_id=None):
        match_book = self.get_match_book(request, book_id)
        match_book_title = match_book["Title"]

        try:
            print("## RENTABOOK ##: Trying to get download link")
            download_link = self.get_download_link(match_book)
            print("## RENTABOOK ##: SUCCESS - Got download link")
            return JsonResponse(
                {"detail": ("Local download complete."), "download_link": download_link}
            )

        except:
            print("## RENTABOOK ##: ERROR - Failed getting download link")
            return JsonResponse(
                {
                    "detail": (
                        "Couldn't find a download link. Try selecting a different file"
                    ),
                    "error": "error",
                }
            )

    def get_match_book(self, request, book_id):
        if request.session["search_results"]:
            for book in request.session["search_results"]:
                if book["ID"] == book_id:
                    request.session["match_book"] = book
                    return book
            return
        else:
            print("Didn't find a match book.")
            return

    def get_download_link(self, match_book):
        mirror_url = match_book["Mirror_1"]

        print("# get_download_link #: Downloading page")
        with urllib.request.urlopen(mirror_url) as download_page:
            download_page_html = download_page.read()

        soup = BeautifulSoup(download_page_html, "html.parser")

        print("# get_download_link #: Getting download link")
        download_link = soup.h2.a.get("href")

        print("# get_download_link #: SUCCESS - Got the download link")

        return download_link
