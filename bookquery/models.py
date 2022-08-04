import math
import re

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db import models
from grab_convert_from_libgen import LibgenSearch


class BookQuery(models.Model):
    # Some static vars
    search_prompt = "Search for book by title, author, or both."

    # Model fields
    search_term = models.CharField(max_length=1000, verbose_name=search_prompt)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="query"
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    pages = models.IntegerField(null=True, blank=True)

    FICTION = "Fiction"
    NON_FICTION = "Non-fiction"

    SEARCH_TYPE_CHOICES = [(FICTION, "Fiction"), (NON_FICTION, "Non-fiction")]
    search_type = models.CharField(
        max_length=500,
        choices=SEARCH_TYPE_CHOICES,
        default=FICTION,
        verbose_name="Choose fiction or non-fiction.",
    )

    def __str__(self):
        try:
            return f"'{self.search_term}' in {self.search_type} by {self.user.username}"
        except AttributeError:
            return f"'{self.search_term}' by unknown user (something is WRONG)."

    ########## ANNOYING LEGACY CODE TO HANDLE NON-FICTION PAGE NUMS ############

    def get_num_pages(self):
        query_parsed = "%20".join(self.search_term.split(" "))
        search_url = f"https://libgen.is/search.php?req={query_parsed}&open-0&res=100&column=def&sort=def&sortmode=ASC&page=1"
        search_page = requests.get(search_url, timeout=5)

        soup = BeautifulSoup(search_page.text, "lxml")

        num_results_tag = soup.find_all("font")
        num_results_string = str(num_results_tag[2])
        num_results = float(re.search(r">(.*?) files", num_results_string).group(1))
        num_pages = int(math.ceil(num_results / 100))

        return num_pages


#############################################################################
