from django import forms 
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SaveCategory(forms.ModelForm):
    name = forms.CharField(max_length="250")
    description = forms.Textarea()
    status = forms.ChoiceField(choices=[('1','Active'),('2','Inactive')])

    class Meta:
        model = Category
        fields = ('name','description', 'status')

    def clean_name(self):
        id = self.instance.id if self.instance.id else 0
        name = self.cleaned_data['name']
        # print(int(id) > 0)
        # raise forms.ValidationError(f"{name} Category Already Exists.")
        try:
            if int(id) > 0:
                category = Category.objects.exclude(id=id).get(name = name)
            else:
                category = Category.objects.get(name = name)
        except:
            return name
            # raise forms.ValidationError(f"{name} Category Already Exists.")
        raise forms.ValidationError(f"{name} Category Already Exists.")

class SaveProduct(forms.ModelForm):
    name = forms.CharField(max_length="250")
    product = forms.CharField(max_length=30)
    description = forms.Textarea()
    status = forms.ChoiceField(choices=[('1','Active'),('2','Inactive')])
    description = forms.CharField(max_length=250)
    category_id = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)  # Use ModelChoiceField

    class Meta:
        model = Products
        fields = ('code','name','category_id','description','status','price')

    def clean_code(self):
        code = self.cleaned_data['code']
        # Check for duplicate code only for new products
        if not self.instance.pk:  # Check if instance exists (new product)
            try:
                Products.objects.get(code=code)
                raise forms.ValidationError(f"{code} Code Already Exists.")
            except Products.DoesNotExist:
                pass  # Code is unique for a new product

        return code
    

class StockHistorySearchForm(forms.ModelForm):
	export_to_CSV = forms.BooleanField(required=False)
	start_date = forms.DateTimeField(required=False)
	end_date = forms.DateTimeField(required=False)
	class Meta:
		model = StockHistory
		fields = ['category', 'item_name', 'start_date', 'end_date']
			


class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class OrderForm(forms.ModelForm):
	class Meta:
		model = Orders
		fields = ['item_name', 'category', 'order_quantity' ]
          
class SaveSupplier(forms.ModelForm):
    supplier_id = forms.CharField(max_length="250")
    supplier_name = forms.CharField(max_length="250")
    description = forms.Textarea()
    address = forms.CharField(max_length="250")
    phone = forms.CharField(max_length="10")
    email = forms.EmailField(max_length="254")
    status = forms.ChoiceField(choices=[('1','Active'),('0','Inactive')])

    class Meta:
        model = Supplier
        fields = ('supplier_id','supplier_name','description', 'address', 'phone', 'email', 'status')

    def clean_name(self):
        id = self.instance.id if self.instance.id else 0
        supplier_name = self.cleaned_data['supplier_name']
        # print(int(id) > 0)
        # raise forms.ValidationError(f"{name} Category Already Exists.")
        try:
            if int(id) > 0:
                supplier = Supplier.objects.exclude(id=id).get(supplier_name = supplier_name)
            else:
                supplier = Supplier.objects.get(supplier_name = supplier_name)
        except:
            return supplier_name
            # raise forms.ValidationError(f"{name} Category Already Exists.")
        raise forms.ValidationError(f"{supplier_name} Supplier Already Exists.")
    
class PurchasesForm(forms.ModelForm):
    purchase_code = forms.CharField(max_length="250")
    supplier =forms.ModelChoiceField(queryset=Supplier.objects.all(), required=True)
    product_name=forms.ModelChoiceField(queryset=Products.objects.all(), required=True)
    class Meta:
        model = Purchases
        fields = ['purchase_code', 'supplier', 'product_name', 'quantity_supplied']