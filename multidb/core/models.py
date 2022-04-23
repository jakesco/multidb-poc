from django.db import models


class Item(models.Model):
    user = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user} - {self.created_at})"
