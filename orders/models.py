from django.db import models


class Order(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)  # updated on create
    updated_at = models.DateTimeField(auto_now=True)  # updated on save

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name


class OrderItem(models.Model):
    product_title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    # related_name='order_items' <-- this allows access from Order to all its OrderItems.
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
