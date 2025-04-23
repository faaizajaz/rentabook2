import math
import re

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db import models
from grab_convert_from_libgen import LibgenSearch
from requests.exceptions import Timeout


class DownloadCount(models.Model):
    num_downloads = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.num_downloads)


class BookQuery(models.Model):
    # Some static vars
    # Idk why I put this search prompt here, but here it will stay.
    search_prompt = "Search for a book by title, author, or both."
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
        "Mirror_2",
        "Mirror_1",
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

    def get_num_pages_non_fiction(self):
        query_parsed = "%20".join(self.search_term.split(" "))
        search_url = f"https://libgen.is/search.php?req={query_parsed}&open-0&res=100&column=def&sort=def&sortmode=ASC&page=1"
        search_page = requests.get(search_url, timeout=10)

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
        search_page = requests.get(search_url, timeout=10)

        soup = BeautifulSoup(search_page.text, "lxml")

        num_results_hold = soup.find_all("div", attrs={"class": "catalog_paginator"})[0]
        results_div = str(num_results_hold.find_next("div"))
        num_results = int("".join(filter(str.isdigit, results_div)))
        num_pages = int(math.ceil(num_results / 25))

        return num_pages

    ########## ANNOYING LEGACY CODE TO HANDLE NON-FICTION ############

    def search_non_fiction(self, num_pages):
        try:
            i = 1
            filtered_data = []
            for page in range(num_pages):
                query_parsed = "%20".join(self.search_term.split(" "))
                search_url = f"https://libgen.is/search.php?req={query_parsed}&open-0&res=100&column=def&sort=def&sortmode=ASC&page={i}"
                search_page = requests.get(search_url, timeout=10)

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

    ####################### END LEGACY CODE ########################

    def search_fiction(self, num_pages):
        try:
            i = 1
            results_list = []
            book_id = 1

            for page in range(num_pages):
                result = LibgenSearch(
                    "fiction",
                    q=self.search_term,
                    language="English",
                    format="epub",
                    page=i,
                ).get_results()

                for book in result:
                    d = {}
                    d["ID"] = str(book_id)
                    d["Author"] = result[book]["author(s)"]
                    # Clean up title
                    title = (
                        result[book]["title"].split("ISBN:", 1)[0].split("ASIN:", 1)[0]
                    )
                    d["Title"] = title
                    size_ext = result[book]["file"].split("/", 1)
                    d["Extension"] = size_ext[0]
                    d["Size"] = size_ext[1]
                    d["Mirror_1"] = result[book]["mirror1"]
                    d["Mirror_2"] = result[book]["mirror2"]
                    # d["Mirror_3"] = result[book]["mirror3"]
                    results_list.append(d)
                    book_id = book_id + 1

            return results_list
        except Timeout:
            return {"timeout": "timeout"}
        except:
            return {"timeout": "timeout"}


# {'ID': '2925862', 'Author': 'G.K. Chesterton', 'Title': 'Appreciations and Criticisms of the Works of Charles Dickens', 'Publisher': 'Amazon Digital Services', 'Year': '2009', 'Pages': '296', 'Language': 'English', 'Size': '251 Kb', 'Extension': 'epub', 'Mirror_1': 'http://library.lol/main/B686081E1C1E5C6222160BC939C9AFDF', 'Mirror_2': 'https://cdn1.booksdl.org/ads.php?md5=B686081E1C1E5C6222160BC939C9AFDF', 'Mirror_3': 'https://3lib.net/md5/B686081E1C1E5C6222160BC939C9AFDF', 'Mirror_4': 'https://library.bz/main/edit/B686081E1C1E5C6222160BC939C9AFDF'},

# {'author(s)': 'Selby, Hubert Jr', 'series': '', 'title': 'Requiem for a Dream', 'language': 'English', 'file': 'EPUB / 227\xa0Kb', 'mirror1': 'http://library.lol/fiction/B5A099FFF1378126EC453794036A1CD0', 'mirror2': 'https://library.bz/fiction/edit/B5A099FFF1378126EC45
