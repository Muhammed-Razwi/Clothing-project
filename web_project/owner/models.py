from django.db import models
# Create your models here.

class owner(models.Model):
    name= models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username



# Size Model
class size(models.Model):
    id = models.AutoField(primary_key=True)
    size_name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.size_name


# Colour Model
class colour(models.Model):
    id = models.AutoField(primary_key=True)
    colour_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.colour_name


#category Model
class category(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category_name


#product model


class owner(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class size(models.Model):
    id = models.AutoField(primary_key=True)
    size_name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.size_name


class colour(models.Model):
    id = models.AutoField(primary_key=True)
    colour_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.colour_name


class category(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    product_name = models.CharField(max_length=150)

    category = models.ForeignKey(category, on_delete=models.PROTECT, related_name="products")
    size = models.ForeignKey(size, on_delete=models.PROTECT, related_name="products")
    colour = models.ForeignKey(colour, on_delete=models.PROTECT, related_name="products")

    front_image = models.CharField(max_length=255, blank=True, null=True)
    back_image = models.CharField(max_length=255, blank=True, null=True)
    side_image = models.CharField(max_length=255, blank=True, null=True)

    quantity = models.PositiveIntegerField(default=0)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return self.product_name

    @property
    def selling_price(self):
        return self.mrp - (self.mrp * self.discount_rate / 100)

    