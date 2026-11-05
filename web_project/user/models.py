
from django.db import models
from owner.models import Product


class user(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    password = models.CharField(max_length=100)

    # User profile image
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.username

# WISHLIST MODEL

class Wishlist(models.Model):
    user = models.ForeignKey(
        'user.user',
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )

    product = models.ForeignKey(
        'owner.Product',
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_wishlist_product'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


# CART MODEL

class CartItem(models.Model):
    user = models.ForeignKey(
        'user.user',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    product = models.ForeignKey(
        'owner.Product',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_cart_product'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


# ORDER MODEL

class Order(models.Model):

    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('ONLINE', 'Online Payment'),
    ]

    STATUS_CHOICES = [
        ('PLACED', 'Order Placed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(
        'user',
        on_delete=models.CASCADE,
        related_name='orders'
    )

    order_number = models.CharField(
        max_length=30,
        unique=True
    )

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=10)

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES
    )

    payment_status = models.CharField(
        max_length=20,
        default='PENDING'
    )

    order_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PLACED'
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number


# ORDER ITEM MODEL

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # Connects directly to the Product table
    product = models.ForeignKey(
        'owner.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordered_items'
    )

    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product_name

