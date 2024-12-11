from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class TodoItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)  # New field for due dates

    class Meta:
        db_table = 'todo_list_todoitem'  # Specify the existing table name

    def __str__(self):
        return self.text