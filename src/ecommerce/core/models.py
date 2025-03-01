from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username  # Display username instead of email


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Prevent duplicate categories
    slug = models.SlugField(unique=True, blank=True)  # SEO-friendly URL identifier

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"  # Correct plural name in admin panel


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)  # Track stock availability
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Track creation time
    is_deleted = models.BooleanField(default=False)  # Soft delete

    def __str__(self):
        return self.name

    def clean(self):
        if self.stock < 0:
            raise ValidationError("Stock cannot be negative.")
        
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='product_name_idx'),
        ]


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)  # Track last modification

    def __str__(self):
        return f"{self.user.username}'s cart - {self.product.name}"

    def clean(self):
        if self.quantity > self.product.stock:
            raise ValidationError("Quantity exceeds available stock.")


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')
    payment_status = models.CharField(max_length=20, choices=[
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
    ], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)  # Track creation time

    @property
    def total_price(self):
        return sum(item.price_at_order * item.quantity for item in self.orderitem_set.all())

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    class Meta:
        indexes = [
            models.Index(fields=['created_at'], name='order_created_at_idx'),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    def save(self, *args, **kwargs):
        if not self.price_at_order:
            self.price_at_order = self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating 1-5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Track creation time

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

    def clean(self):
        if not OrderItem.objects.filter(order__user=self.user, product=self.product).exists():
            raise ValidationError("You can only review products you've purchased.")