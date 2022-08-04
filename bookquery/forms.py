from django.forms import ChoiceField, ModelForm, RadioSelect

from .models import BookQueryNonFiction


class BookQueryForm(ModelForm):
    SEARCH_TYPE_CHOICES = [("Fiction", "Fiction"), ("Non-fiction", "Non-fiction")]
    search_type = ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        widget=RadioSelect(),
        label="Choose fiction or non-fiction.",
        initial="Fiction",
    )

    class Meta:
        model = BookQueryNonFiction
        exclude = ["user", "pages"]