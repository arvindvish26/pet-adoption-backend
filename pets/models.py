from django.db import models
from accessories.models import Category
from users.models import User

class Pet(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Adopted', 'Adopted'),
    )
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    breed = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    vaccinated = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Available')
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.breed})"
