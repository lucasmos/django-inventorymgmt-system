from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.


class Category(models.Model):
	name = models.CharField(max_length=50, blank=True, null=True)
	description = models.TextField()
	status = models.IntegerField(default=1)
	date_added = models.DateTimeField(default=timezone.now)
	date_updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name


class Products(models.Model):
	code = models.CharField(max_length=100)
	category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
	name = models.TextField()
	quantity = models.PositiveIntegerField(default='0', blank=True, null=True)
	description = models.TextField()
	price = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.IntegerField(default=1)
	reorder_level = models.PositiveIntegerField(default=0)
	date_added = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.code + " - " + self.name

	def count_inventory(self):
		stocks = Stock.objects.filter(product=self)
		stockIn = 0
		stockOut = 0
		for stock in stocks:
			if stock.type == '1':
				stockIn = int(stockIn) + int(stock.quantity)
			else:
				stockOut = int(stockOut) + int(stock.quantity)
		available = stockIn - stockOut
		return available


class Stock(models.Model):
	product = models.ForeignKey(Products, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default='0', blank=True, null=True)
	type = models.CharField(max_length=2, choices=(('1', 'Stock-in'), ('2', 'Stock-Out')), default=1)
	date_created = models.DateTimeField(default=timezone.now)
	date_updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.product.code + ' - ' + self.product.name


class StockHistory(models.Model):
	item_ID = models.CharField(max_length=50, blank=True, null=True)
	item_name = models.CharField(max_length=50, blank=True, null=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
	quantity = models.IntegerField(default='0', blank=True, null=True)  # type: ignore
	receive_quantity = models.IntegerField(default='0', blank=True, null=True)  # type: ignore
	receive_by = models.CharField(max_length=50, blank=True, null=True)
	issue_quantity = models.IntegerField(default='0', blank=True, null=True)  # type: ignore
	issue_by = models.CharField(max_length=50, blank=True, null=True)
	issue_to = models.CharField(max_length=50, blank=True, null=True)
	created_by = models.CharField(max_length=50, blank=True, null=True)
	reorder_level = models.IntegerField(default='0', blank=True, null=True)  # type: ignore
	timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
	last_updated = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
	price = models.DecimalField(max_digits=10, decimal_places=2)


class Orders(models.Model):
	item_name = models.CharField(max_length=50, blank=True, null=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
	order_quantity = models.PositiveIntegerField(default='0', blank=True, null=True)  # type: ignore
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
	staff = models.ForeignKey(User, models.CASCADE, null=True)

	def __str__(self):
		return f'{self.item_name} ordered by {self.staff.username}'


class Sales(models.Model):
	code = models.CharField(max_length=100)
	sub_total = models.DecimalField(max_digits=10, decimal_places=2)
	grand_total = models.DecimalField(max_digits=10, decimal_places=2)
	tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
	tax = models.DecimalField(max_digits=10, decimal_places=2)
	tendered_amount = models.DecimalField(max_digits=10, decimal_places=2)
	amount_change = models.DecimalField(max_digits=10, decimal_places=2)
	timestamp = models.DateTimeField(default=timezone.now)
	last_updated = models.DateTimeField(auto_now=True)
	transaction_code = models.CharField(max_length=8, unique=True)

	def __str__(self):
		return self.code


class SalesItems(models.Model):
	sale_id = models.ForeignKey(Sales, on_delete=models.CASCADE)
	product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	qty = models.DecimalField(max_digits=10, decimal_places=2)
	total_sales = models.DecimalField(max_digits=10, decimal_places=2)
	transaction_code = models.CharField(max_length=8, unique=True)

class Supplier(models.Model):
	supplier_id = models.CharField(max_length=200)
	supplier_name = models.CharField(max_length=150)
	description = models.TextField()
	phone = models.CharField(max_length=10, unique=True)
	address = models.CharField(max_length=200)
	email = models.EmailField(max_length=254, unique=True)
	status = models.IntegerField(default=1)

	def __str__(self):
		return self.supplier_id
	
class Purchases(models.Model):
	purchase_code = models.CharField(max_length=100)
	supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
	product_name = models.ForeignKey(Products, on_delete=models.CASCADE)
	quantity_supplied = models.PositiveIntegerField(default='0', blank=True, null=True)
	date_added = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.purchase_code
	
class MPesaTransaction(models.Model):
    """
    Model representing an M-Pesa transaction.
    """
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    amount = models.IntegerField(verbose_name="Amount")
    account_reference = models.CharField(max_length=50, verbose_name="Account Reference")
    transaction_desc = models.CharField(max_length=255, verbose_name="Transaction Description")

    class Meta:
        """Meta options for the MPesaTransaction model."""
        verbose_name = "M-Pesa Transaction"
        verbose_name_plural = "M-Pesa Transactions"

    def __str__(self):
        """
        String representation of the M-Pesa transaction.
        """
        return f"{self.phone_number} - {self.amount}"