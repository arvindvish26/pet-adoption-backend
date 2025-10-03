from django.db import models
from users.models import User
from accessories.models import Accessory

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Cart #{self.id} for {self.user.username}"

class CartAccessory(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_accessories')
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"{self.quantity} x {self.accessory.name} in cart {self.cart.id}"
