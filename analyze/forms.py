from django import forms
from .models import Text

class TextUploadForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = ['content']