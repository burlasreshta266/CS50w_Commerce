from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return f"{self.name}"
    
class Bid(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", default="not found")
    def __str__(self):
        return f"${self.price} by {self.user}"
    
class Listing(models.Model):
    title = models.CharField(max_length=40)
    description = models.TextField(max_length=300)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", default="not found")
    price = models.DecimalField(decimal_places=2, max_digits=10)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings", default="not defined")
    imageURL = models.CharField(default="none")
    active = models.BooleanField(default=True)
    latest_bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="listings", default=1.00)
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watchlisted")

    def __str__(self):
        return f"{self.title}"
    
class Comment(models.Model):
    title = models.CharField(max_length=70)
    content = models.TextField(max_length=700)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", default="not found")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Comments", default="not found")
    def __str__(self):
        return f"{self.title}"
   