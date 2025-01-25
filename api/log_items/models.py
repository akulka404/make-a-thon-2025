# log_items/models.py
from django.db import models
from datetime import date

class FOOD_DATA(models.Model):
    food_id = models.AutoField(primary_key=True)
    food_name = models.CharField(max_length=100, blank=False, default='')

    REGISTER_CHOICES = (
        ('G', 'Good. Can be used.'),
        ('R', 'Rotten'),
        ('/', 'Prefer not to say'),
    )
    food_quality = models.CharField(max_length=1, choices=REGISTER_CHOICES)
    # food_best_before = models.CharField(max_length=100, blank=False, default='')

    # auto_now_add=True => set this *once* at row creation
    stored_date = models.DateField(auto_now_add=True)
    stored_time = models.TimeField(auto_now_add=True)

    # no auto_ here: we’ll compute these ourselves below
    expired_date = models.DateField(blank=True, null=True)
    expired_time = models.TimeField(blank=True, null=True)

    REGISTER_CHOICES1 = (
        ('U', 'Can use. Still good for storage'),
        ('Q', 'Use quickly. Will go bad soon'),
        ('T', 'Throw away'),
        ('C', 'Compost'),
    )
    food_usage = models.CharField(max_length=1, choices=REGISTER_CHOICES1)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.food_name} (ID: {self.food_id})"
