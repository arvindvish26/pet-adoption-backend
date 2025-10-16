from django.db import models
from accessories.models import Category
from users.models import User

class Pet(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Adopted', 'Adopted'),
    )
    CURRENCY_CHOICES = [
        ('INR', 'Indian Rupee'),
        ('USD', 'US Dollar'),
    ]
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    breed = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    vaccinated = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Available')
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets', null=True, blank=True)
    adoption_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')

    def __str__(self):
        return f"{self.name} ({self.breed})"
    
    @property
    def formatted_adoption_fee(self):
        """Return formatted adoption fee with currency symbol"""
        if self.currency == 'INR':
            return f"₹{self.adoption_fee}"
        elif self.currency == 'USD':
            return f"${self.adoption_fee}"
        return f"{self.currency} {self.adoption_fee}"
