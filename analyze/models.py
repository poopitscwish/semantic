from django.db import models

class Text(models.Model):
    content = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = 'analyze' 