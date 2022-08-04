import math
import re

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db import models
from grab_convert_from_libgen import LibgenSearch
from requests.exceptions import Timeout


class BookQuery(models.Model):
    # Some static vars
    search_prompt = "Search for book by title, author, or both."
    col_names_non_fiction = [
        "ID",
        "Author",
        "Title",
        "Publisher",
        "Year",
        "Pages",
        "Language",
        "Size",
        "Extension",
        "Mirror_1",
        "Mirror_2",
        "Mirror_3",
        "Mirror_4",
        "Mirror_5",
        "Edit",
    ]

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

    def get_num_pages_non_fiction(self):
        query_parsed = "%20".join(self.search_term.split(" "))
        search_url = f"https://libgen.is/search.php?req={query_parsed}&open-0&res=100&column=def&sort=def&sortmode=ASC&page=1"
        search_page = requests.get(search_url, timeout=5)

        soup = BeautifulSoup(search_page.text, "lxml")

        num_results_tag = soup.find_all("font")
        num_results_string = str(num_results_tag[2])
        num_results = float(re.search(r">(.*?) files", num_results_string).group(1))
        num_pages = int(math.ceil(num_results / 100))

        return num_pages

    def get_num_pages_fiction(self):
        query_parsed = "%20".join(self.search_term.split(" "))
        search_url = (
            f"https://libgen.is/fiction/?q={query_parsed}&language=English&format=epub"
        )
        search_page = requests.get(search_url, timeout=5)

        soup = BeautifulSoup(search_page.text, "lxml")

        num_results_hold = soup.find_all("div", attrs={"class": "catalog_paginator"})[0]
        results_div = str(num_results_hold.find_next("div"))
        num_results = int("".join(filter(str.isdigit, results_div)))
        num_pages = int(math.ceil(num_results / 25))

        return num_pages

    ############################################################################

    def search_non_fiction(self, num_pages):
        try:
            i = 1
            filtered_data = []
            for page in range(num_pages):

                query_parsed = "%20".join(self.search_term.split(" "))
                search_url = f"https://libgen.is/search.php?req={query_parsed}&open-0&res=100&column=def&sort=def&sortmode=ASC&page={i}"
                search_page = requests.get(search_url, timeout=5)

                soup = BeautifulSoup(search_page.text, "lxml")
                # print(page)

                self.strip_i_tag_from_soup(soup)

                information_table = soup.find_all("table")[2]

                raw_data = [
                    [
                        td.a["href"]
                        if td.find("a")
                        and td.find("a").has_attr("title")
                        and td.find("a")["title"] != ""
                        else "".join(td.stripped_strings)
                        for td in row.find_all("td")
                    ]
                    for row in information_table.find_all("tr")[
                        1:
                    ]  # Skip row 0 as it is the headings row
                ]

                output_data = [
                    dict(zip(self.col_names_non_fiction, row)) for row in raw_data
                ]

                for d in output_data:
                    if d["Extension"] == "epub":
                        filtered_data.append(d)

                i = i + 1
            data = filtered_data

            return data
        except Timeout:
            return {"timeout": "timeout"}
        except:
            return {"timeout": "timeout"}

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()
