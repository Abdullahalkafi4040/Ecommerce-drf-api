from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
user = get_user_model ()

class Category(models.Model):
    name = models.CharField(max_length=100 , unique = True)
    slug =  models.SlugField(max_length=100 , unique = True)

    class Meta :
        verbose_name_plural = 'Categories'
    def __str__(self):
        return self.name

class Product(models.Model):
    category =  models.ForeignKey(Category,on_delete=models.CASCADE , related_name='product')
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True , null = True)
    price = models.DecimalField(max_digits=10 , decimal_places=2)
    stock = models.PositiveIntegerField(default = 0)
    image = models.ImageField(upload_to ='products/' , blank = True,null = True)
    created_at = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return self.name
class Cart(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE , related_name = 'cart')
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.user.username}-এর কার্ট"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart , on_delete=models.CASCADE , related_name = 'items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE )
    quantity =  models.PositiveIntegerField(default=1)
    class Meta:
        unique_together = ['cart' , 'product']

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"  

class Order(models.Model):
    class StatusChoices (models.TextChoices):
        PENDING = 'PENDING' , 'pending'
        PROCESSING = 'PROCESSING' , 'processing'
        SHIPPED = 'SHIPPED' , 'shipped'
        DELIVERED = 'DELIVERED' , 'delivered'

    class PaymentStatusChoices(models.TextChoices):

        UNPAID = 'UNPAID' , 'unpaid'
        PAID = 'PAID' , 'paid'
        FAIL = 'FAILED' , 'failed'

    user = models.ForeignKey(user,on_delete=models.CASCADE , related_name='orders')
    total_price = models.DecimalField(max_digits = 10 , decimal_places = 2 ,default = 0.00)
    status = models.CharField(max_length=200 , choices = StatusChoices.choices , default = StatusChoices.PENDING)
    payment_status = models.CharField(max_length=100, choices=PaymentStatusChoices.choices , default=PaymentStatusChoices.UNPAID)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"অর্ডার #{self.id} - {self.user.username}"
    

  
class OrderItem(models.Model):
    order = models.ForeignKey(Order , on_delete=models.CASCADE , related_name ='items')
    product = models.ForeignKey(Product, on_delete = models.CASCADE )
    price = models.DecimalField(max_digits=10 , decimal_places=2)
    quantity = models.PositiveIntegerField(default = 1)
   
    def __str__(self):
        return f"{self.product.name} ({self.quantity} টি )"

     