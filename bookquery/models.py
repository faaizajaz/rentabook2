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

    def get_num_pages(self, option):
        return
