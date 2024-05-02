import csv
import datetime
import json
import random
import string
import sys
from decimal import Decimal
from io import BytesIO

from django.contrib import messages, auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import get_template
from django.urls import reverse
from xhtml2pdf import pisa
from django.db.models import Sum
from django.db import transaction as db_transaction
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django_daraja.mpesa.core import MpesaClient
from django.conf import settings
import base64
import hashlib



from .forms import *

context = {
    'page_title': 'File Management System',
}


# Create your views here.
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('/login')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    context = {
        "register_form": form,
    }
    return render(request, "register.html", context)


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    context = {
        "login_form": form,
    }
    return render(request, "login.html", context)


def logout_request(request):
    auth.logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('/login')


@login_required
def home(request):      
        labels = []
        data = []        
        stockqueryset = Products.objects.all().order_by('-quantity')
        for item in stockqueryset:
            labels.append(item.name)
            data.append(item.quantity)
        sales = Sales.objects.all().order_by('-timestamp')[:3]
        purchases = Purchases.objects.order_by('-date_added')[:3]
         # calculate item_count for each sale
        for sale in sales:
            sale.item_count = len(SalesItems.objects.filter(sale_id=sale.id).all())
        context = {
            'labels'    : labels,
            'data'      : data,
            'sales'     : sales,
            'purchases' : purchases
        }
        return render(request, "home.html", context)



@login_required
def staff(request):
    workers = User.objects.all()
    workers_count = workers.count()
    orders_count = Orders.objects.all().count()
    products_count = Products.objects.all().count()
    context = {
        "workers": workers,
        "workers_count": workers_count,
        "orders_count": orders_count,
        "products_count": products_count,
    }
    return render(request, "staff.html", context)


@login_required
def order(request):
    orders = Orders.objects.all()
    workers_count = User.objects.all().count()
    orders_count = Orders.objects.all().count()
    products_count = Products.objects.all().count()
    context = {
        "orders": orders,
        "workers_count": workers_count,
        "orders_count": orders_count,
        "products_count": products_count,
    }
    return render(request, 'order.html', context)


@login_required
def category(request):
    category_list = Category.objects.all()
    # category_list = {}
    context = {
        'page_title': 'Category List',
        'category': category_list,
    }
    return render(request, 'category.html', context)


@login_required
def manage_category(request, pk=None):
    context['page_title'] = "Manage Category"
    if not pk is None:
        category = Category.objects.get(id=pk)
        context['category'] = category
    else:
        context['category'] = {}
    return render(request, 'manage_category.html', context)


@login_required
def save_category(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            category = Category.objects.get(pk=request.POST['id'])
        else:
            category = None
        if category is None:
            form = SaveCategory(request.POST)
        else:
            form = SaveCategory(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def delete_category(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        try:
            category = Category.objects.get(id=request.POST['id'])
            category.delete()
            messages.success(request, 'Category has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'Category has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Category has failed to delete'

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def product(request):
    product_list = Products.objects.all()
    context = {
        'page_title': 'Product List',
        'products': product_list,
    }
    return render(request, 'product.html', context)


@login_required
def manage_product(request):
    product = {}
    categories = Category.objects.filter(status=1).all()
    if request.method == 'GET':
        data = request.GET
        id = ''
        if 'id' in data:
            id = data['id']
        if id.isnumeric() and int(id) > 0:
            product = Products.objects.filter(id=id).first()

    context = {
        'product': product,
        'categories': categories
    }
    return render(request, 'manage_product.html', context)


def test(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'test.html', context)


@login_required
def save_product(request):
    data = request.POST
    resp = {'status': 'failed'}
    id = ''
    if 'id' in data:
        id = data['id']
    if id.isnumeric() and int(id) > 0:
        check_code = Products.objects.exclude(id=id).filter(code=data['code']).all()
        check_name = Products.objects.exclude(id=id).filter(name=data['name']).all()
    else:
        check_code = Products.objects.filter(code=data['code']).all()
        check_name = Products.objects.filter(name=data['name']).all()
    if len(check_code) > 0:
        resp['msg'] = "Product Code Already Exists in the database"
    elif len(check_name) > 0:
        resp['msg'] = "Product Name Already Exists in the database"
    else:
        category = Category.objects.filter(id=data['category_id']).first()
        try:
            if (data['id']).isnumeric() and int(data['id']) > 0:
                product = Products.objects.filter(id=data['id']).first()
                old_quantity = product.quantity
                Products.objects.filter(id=data['id']).update(code=data['code'], category_id=category,
                                                              name=data['name'],
                                                              quantity=data['quantity'],
                                                              reorder_level=data['reorder_level'],
                                                              description=data['description'],
                                                              price=Decimal(data['price']),
                                                              date_updated=timezone.now(),
                                                              status=data['status'])
                messages.success(request, f'Product Successfully updated. Quantity updated from {old_quantity} to {data["quantity"]}.')
            else:
                save_product = Products(code=data['code'], category_id=category, name=data['name'],
                                        quantity=data['quantity'], description=data['description'],
                                        reorder_level=data['reorder_level'], price=Decimal(data['price']),
                                        date_added=timezone.now(), date_updated=timezone.now(), status=data['status'])
                save_product.save()
                messages.success(request, 'Product Successfully saved.')
            resp['status'] = 'success'
        except:
            resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_product(request):
    data = request.POST
    resp = {'status': ''}
    try:
        Products.objects.filter(id=data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def list_history(request):
    header = 'HISTORY DATA'
    queryset = StockHistory.objects.all()
    form = StockHistorySearchForm(request.POST or None)
    context = {
        "header": header,
        "queryset": queryset,
        "form": form,
    }
    if request.method == 'POST':
        form = StockHistorySearchForm(request.POST or None)
        category = form['category'].value()
        item_name = form['item_name'].value()
        start_date = form['start_date'].value()
        end_date = form['end_date'].value()
        queryset = StockHistory.objects.filter(
            item_name__icontains=item_name,
            last_updated__range=[
                start_date,
                end_date
            ]
        )

        if category != '':
            queryset = queryset.filter(category_id=category)
        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
            writer = csv.writer(response)
            writer.writerow(
                ['CATEGORY',
                 'ITEM NAME',
                 'QUANTITY IN STOCK',
                 'ISSUE QUANTITY',
                 'RECEIVE QUANTITY',
                 'RECEIVE BY',
                 'ISSUE BY',
                 'LAST UPDATED'])
            instance = queryset
            for stock in instance:
                writer.writerow(
                    [stock.category,
                     stock.item_name,
                     stock.quantity,
                     stock.issue_quantity,
                     stock.receive_quantity,
                     stock.receive_by,
                     stock.issue_by,
                     stock.last_updated])
            return response
    context = {
        "form": form,
        "header": header,
        "queryset": queryset,
    }
    return render(request, "list_history.html", context)


@login_required
def pos(request):
    products = Products.objects.filter(status=1)
    product_json = []
    for product in products:
        product_json.append(
            {'id': product.id, 'name': product.name, 'price': float(product.price), 'quantity': product.quantity,
             'reorder_level': product.reorder_level})
    context = {
        'page_title': "Point of Sale",
        'products': products,
        'product_json': json.dumps(product_json)
    }
    # return HttpResponse('')
    return render(request, 'pos.html', context)


@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total': grand_total,
    }
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method == 'cash':
            # Process cash payment and redirect to the save_pos view
            return redirect('save_pos')
        elif payment_method == 'mpesa':
            # Redirect to mpesa view to finalize the payment
            return redirect('mpesa', amount=grand_total)
    return render(request, 'checkout_modal.html', context)

@login_required
def save_pos(request):
    resp = {'status': 'failed', 'msg': ''}
    data = request.POST
    pref = str(datetime.datetime.now().year)
    transaction_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        i += int(1)
        check = Sales.objects.filter(code=pref + code).all()
        if len(check) <= 0:
            break
    code = str(pref) + str(code)

    try:
        with db_transaction.atomic():
            sale = Sales(
                transaction_code=transaction_code,
                code=code,
                sub_total=Decimal(data.get('sub_total')),
                tax=Decimal(data.get('tax')),
                tax_amount=Decimal(data.get('tax_amount')),
                grand_total=Decimal(data.get('grand_total')),
                tendered_amount=Decimal(data.get('tendered_amount')),
                amount_change=Decimal(data.get('amount_change'))
            )
            sale.save()

            sale_id = sale.pk

            for product_id, qty, price in zip(data.getlist('product_id[]'), data.getlist('qty[]'), data.getlist('price[]')):
                product = get_object_or_404(Products, id=product_id)
                qty = Decimal(qty)
                price = Decimal(price)
                total_sales = qty * price

                if qty > product.quantity:
                    resp['msg'] = f"Product '{product.name}' has insufficient stock level. Only {product.quantity} items are available."
                    raise ValueError(resp['msg'])

                # Deduct the quantity sold from the stock quantity
                product.quantity -= qty
                product.save()

                transaction_code_item = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                SalesItems(
                    transaction_code=transaction_code_item,
                    sale_id=sale,
                    product_id=product,
                    qty=qty,
                    price=price,
                    total_sales=total_sales
                ).save()

            resp['status'] = 'success'
            resp['sale_id'] = sale_id
            messages.success(request, "Sale Record has been saved.")
            messages.success(request, f"Quantity remaining in stock for each product: {product.quantity}")
    except Exception as e:
        resp['msg'] = str(e)

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def sales_list(request):
    sales = Sales.objects.all()
    sale_data = []
    for sale in sales:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale, field.name)
        data['transaction_code'] = sale.transaction_code  # retrieve the transaction code
        items = SalesItems.objects.filter(sale_id=sale).values('product_id__name', 'qty', 'price', 'total_sales')
        data['items'] = [{'Product Name': item['product_id__name'], 'Quantity': item['qty'], 'Price': item['price'], 'Total Sales': item['total_sales']} for item in items]
        data['item_count'] = len(data['items'])
        if 'tax_amount' in data:
            data['tax_amount'] = format(Decimal(data['tax_amount']), '.2f')
        sale_data.append(data)

    if request.GET.get('format') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_list.csv"'
        writer = csv.DictWriter(response, fieldnames=sale_data[0].keys())
        writer.writeheader()
        for sale in sale_data:
            writer.writerow(sale)
        return response

    
    if request.GET.get('format') == 'pdf':
        template = get_template('sales_list_pdf.html')
        page_num = int(request.GET.get('page', 1))
        html = template.render({'sale_data': sale_data, 'page_num': page_num, 'now': datetime.datetime.now()})
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
            return response
        return HttpResponse('Error generating PDF')

    context = {
        'page_title': 'Sales Transactions',
        'sale_data': sale_data,
    }
    return render(request, 'sales_list.html', context)


@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id=id).first()
    # Generate a unique transaction code
    transaction = {}
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales, field.name)
            transaction['transaction_code'] = sales.transaction_code  # retrieve the transaction code
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(Decimal(transaction['tax_amount']))
    ItemList = SalesItems.objects.filter(sale_id=sales).all()
    context = {
        "transaction": transaction,
        "SalesItems": ItemList,

    }

    return render(request, 'receipt.html', context)
    # return HttpResponse('')


@login_required
def delete_sale(request):
    resp = {'status': 'failed', 'msg': ''}
    id = request.POST.get('id')
    try:
        delete = Sales.objects.filter(id=id).delete()
        resp['status'] = 'success'
        messages.success(request, 'Sale Record has been deleted.')
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')

@login_required
def supplier(request):
    supplier_list = Supplier.objects.all()
    context = {
        'page_title': 'Supplier List',
        'supplier': supplier_list,
    }
    return render(request, 'supplier.html', context)


@login_required
def manage_supplier(request, pk=None):
    context['page_title'] = "Manage Supplier"
    if not pk is None:
        supplier = Supplier.objects.get(id=pk)
        context['supplier'] = supplier
    else:
        context['supplier'] = {}
    return render(request, 'manage_supplier.html', context)


@login_required
def save_supplier(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            supplier = Supplier.objects.get(pk=request.POST['id'])
        else:
            supplier = None
        if supplier is None:
            form = SaveSupplier(request.POST)
        else:
            form = SaveSupplier(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def delete_supplier(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        try:
            supplier = Supplier.objects.get(id=request.POST['id'])
            supplier.delete()
            messages.success(request, 'Supplier has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'Supplier has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Supplier has failed to delete'

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def purchases(request):
    purchase_list = Purchases.objects.all()
    context = {
        'page_title': 'Purchases List',
        'purchases': purchase_list,
    }
    return render(request, 'purchases.html', context)

@login_required
def manage_purchase(request):
    purchase = {}
    suppliers = Supplier.objects.all()
    products = Products.objects.all()
    if request.method == 'GET':
        data = request.GET
        id = ''
        if 'id' in data:
            id = data['id']
        if id.isnumeric() and int(id) > 0:
            purchase = Purchases.objects.filter(id=id).first()

    context = {
        'purchase': purchase,
        'suppliers': suppliers,
        'products': products
    }
    return render(request, 'manage_purchase.html', context)

@login_required
def purchasetest(request):
    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers
    }
    return render(request, 'purchasetesttest.html', context)

@login_required
def save_purchase(request):
    data = request.POST
    resp = {'status': 'failed'}
    id = ''
    if 'id' in data:
        id = data['id']
    if id.isnumeric() and int(id) > 0:
        check = Purchases.objects.exclude(id=id).filter(purchase_code=data['purchase_code']).all()
    else:
        check = Purchases.objects.filter(purchase_code=data['purchase_code']).all()
    if len(check) > 0:
        resp['msg'] = "Purchase Code Already Exists in the database"
    else:
        product = Products.objects.filter(id=data['product_name']).first()
        suppliers = Supplier.objects.filter(id=data['supplier']).first()
        quantity_supplied = data['quantity_supplied']
        try:
            if (data['id']).isnumeric() and int(data['id']) > 0:
                old_quantity_supplied = Purchases.objects.filter(id=data['id']).first().quantity_supplied
                Purchases.objects.filter(id=data['id']).update(purchase_code=data["purchase_code"],
                                                              supplier=suppliers, product_name=product,
                                                              quantity_supplied=data['quantity_supplied'],
                                                              date_updated=timezone.now())
                new_quantity = product.quantity + int(quantity_supplied) - int(old_quantity_supplied)
                product.quantity = new_quantity
                product.date_updated = timezone.now()
                product.save()
                messages.success(request, f'Purchase Successfully updated. Product quantity increased from {product.quantity - int(quantity_supplied) + int(old_quantity_supplied)} to {product.quantity}.')
            else:
                save_purchase = Purchases(purchase_code=data['purchase_code'], supplier=suppliers,
                                          product_name=product, quantity_supplied=data['quantity_supplied'],
                                          date_added=timezone.now(), date_updated=timezone.now())
                save_purchase.save()
                old_quantity = product.quantity
                product.quantity += int(quantity_supplied)
                product.date_updated = timezone.now()
                product.save()
                messages.success(request, f'Purchase Successfully saved. Product quantity increased from {old_quantity} to {product.quantity}.')
            resp['status'] = 'success'
        except:
            resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_purchase(request):
    data = request.POST
    resp = {'status': ''}
    try:
        purchase = Purchases.objects.filter(id=data['id']).first()
        product = purchase.product_name
        quantity_supplied = purchase.quantity_supplied
        old_quantity = product.quantity
        if product.quantity >= quantity_supplied:
            product.quantity -= quantity_supplied
        else:
            product.quantity = 0
        product.date_updated = timezone.now()
        product.save()
        purchase.delete()
        messages.success(request, f'Purchase Successfully deleted. Product quantity reduced from {old_quantity} to {product.quantity}.')
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")
