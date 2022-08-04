from django.forms import ChoiceField, ModelForm, RadioSelect

from .models import BookQuery


class BookQueryForm(ModelForm):
    SEARCH_TYPE_CHOICES = [("Fiction", "Fiction"), ("Non-fiction", "Non-fiction")]
    search_type = ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        widget=RadioSelect(),
        label="",
        initial="Fiction",
    )

    class Meta:
        model = BookQuery
        exclude = ["user", "pages"]
