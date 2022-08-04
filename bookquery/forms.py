from django.forms import ModelForm

from .models import BookQuery


class BookQueryForm(ModelForm):
    class Meta:
        model = BookQuery
        exclude = ["user", "pages"]
