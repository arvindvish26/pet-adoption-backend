from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Accessory(models.Model):
    CURRENCY_CHOICES = [
        ('INR', 'Indian Rupee'),
        ('USD', 'US Dollar'),
    ]
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')
    stock = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='accessories')
    image = models.ImageField(upload_to='accessories/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    @property
    def formatted_price(self):
        """Return formatted price with currency symbol"""
        if self.currency == 'INR':
            return f"₹{self.price}"
        elif self.currency == 'USD':
            return f"${self.price}"
        return f"{self.currency} {self.price}"
