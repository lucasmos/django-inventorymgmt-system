"""djangoproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from stockmgmt import views


urlpatterns = [
	path('', views.home, name='home'),
    path('category',views.category,name='category'),
    path('manage_category',views.manage_category,name='manage_category'),
    path('save_category',views.save_category,name='save_category'),
    path('manage_category/<int:pk>',views.manage_category,name='manage_category-pk'),
    path('delete_category',views.delete_category,name='delete_category'),
    path('product',views.product,name='product'),
    path('manage_product',views.manage_product,name='manage_product'),
    path('save_product',views.save_product,name='save_product'),
    path('manage_product/<int:pk>',views.manage_product,name='manage_product-pk'),
    path('delete_product',views.delete_product,name='delete_product'),
    path('test', views.test, name="test"),
    #path('stock_detail/<str:pk>/', views.stock_detail, name="stock_detail"),
    #path('reorder_level/<str:pk>/', views.reorder_level, name="reorder_level"),
    path('checkout_modal', views.checkout_modal, name="checkout_modal"),
    path('pos', views.pos, name="pos"),
    path('save_pos', views.save_pos, name="save_pos"),
    path('sales_list', views.sales_list, name="sales_list"),
    path('receipt', views.receipt, name="receipt"),
    path('delete_sale', views.delete_sale, name="delete_sale"),
    path('list_history/', views.list_history, name='list_history'),
    path('supplier',views.supplier,name='supplier'),
    path('manage_supplier',views.manage_supplier,name='manage_supplier'),
    path('save_supplier',views.save_supplier,name='save_supplier'),
    path('manage_supplier/<int:pk>',views.manage_supplier,name='manage_supplier-pk'),
    path('delete_supplier',views.delete_supplier,name='delete_supplier'),
    path('purchases',views.purchases,name='purchases'),
    path('manage_purchase',views.manage_purchase,name='manage_purchase'),
    path('purchasetest', views.purchasetest, name="purchasetest"),
    path('save_purchase',views.save_purchase,name='save_purchase'),
    path('manage_purchase/<int:pk>',views.manage_purchase,name='manage_purchase-pk'),
    path('delete_purchase',views.delete_purchase,name='delete_purchase'),
    path('admin/', admin.site.urls),
    path('register/', views.register_request, name="register"),
    path('login/', views.login_request, name="login"),
    path('logout/', views.logout_request, name= "logout"),
    path('staff/', views.staff, name="staff"),
    path('order/', views.order, name='order'),
]
