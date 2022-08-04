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

    def __str__(self):
        try:
            return f"'{self.search_term}' by {self.user.username}"
        except AttributeError:
            return f"'{self.search_term}' by unknown user (something is WRONG)."
