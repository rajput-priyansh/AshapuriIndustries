from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import format_html
from account.models import Account, SettingAccount, SettingGST

from django.db.models.signals import post_save
from django.dispatch import receiver


class Unit(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, help_text="Unit name e.i. KG, GM")
    description = models.TextField(null=True, blank=True, help_text="Write about the unit")

    def __unicode__(self):
        return self.name.encode('ascii', 'replace')


class ProductSize(models.Model):
    size = models.CharField(max_length=50, null=False, blank=False, help_text="Product size e.i 8 * 10")
    description = models.TextField(null=True, blank=True, help_text="Write about the size")

    def __unicode__(self):
        return self.size.encode('ascii', 'replace')


class Product(models.Model):
    product_name = models.CharField(max_length=100, blank=False, null=False, help_text="Product simple Name")
    product_type = models.CharField(max_length=50, help_text="Product Type")
    hsn_number = models.CharField(max_length=10, blank=True, null=True, help_text='HSN/ACS number')

    def __unicode__(self):
        return self.product_name.encode('ascii', 'replace')


class CustomerOrder(models.Model):
    ORDER_PLACED = 'Placed'
    ORDER_READY = 'Ready'
    ORDER_DELIVERED = 'Delivered'

    ORDER_STATUS_CHOICES = (
        (1, ORDER_PLACED),
        (2, ORDER_READY),
        (3, ORDER_DELIVERED),
    )
    INVOICE_ORIGINAL = 'Original for  Recipient'
    INVOICE_DUPLICATE = 'Duplicate for supplier/Transporter'
    INVOICE_TRIPLICATE = 'Triplicate for Supplier'

    INVOICE_CHOICES = (
        (1, INVOICE_ORIGINAL),
        (2, INVOICE_DUPLICATE),
        (3, INVOICE_TRIPLICATE),
    )
    user = models.ForeignKey(Account, related_name='customer')
    creation_date = models.DateTimeField('date created', auto_now_add=True)
    modified_date = models.DateTimeField('date last modified', auto_now=True)
    delivery_date = models.DateTimeField('date delivery', blank=True, default=timezone.now)
    status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=1)
    invoice_type = models.IntegerField(choices=INVOICE_CHOICES, default=1)
    order_products = models.ManyToManyField(Product, through='OrderProducts')
    description = models.TextField(null=True, blank=True, help_text="Extra details about the order")
    shipping_address = models.TextField(null=False, blank=False, default='Vadodara',
                                        help_text="Destination point where the items is to be delivered",
                                        verbose_name="Place Of Supply")
    state = models.CharField(max_length=50, help_text="State Name", default="Gujrat")
    state_code = models.CharField(max_length=10, help_text="State Code", default="24")
    total = models.FloatField(default=0)
    cgst = models.FloatField(default=0)
    sgst = models.FloatField(default=0)
    igst = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    net_total = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    transportation_mode = models.CharField(max_length=50, help_text="Transportation Mode", default="A")
    vehicle_number = models.CharField(max_length=50, help_text="Vehicle Number", default="A")
    consignee_name = models.CharField(max_length=250, help_text="Consignee Full Name", blank=True, null=True)
    consignee_address = models.CharField(max_length=350, help_text="Consignee Full Address", blank=True, null=True)
    consignee_pan = models.CharField(max_length=50, help_text="Consignee PAN CARD number", blank=True, null=True)
    consignee_gst = models.CharField(max_length=100, help_text="Consignee GST number", blank=True, null=True)
    order_number = models.CharField(max_length=100, help_text="Order number", blank=True, null=True)
    invoice_date = models.DateTimeField('invoice date', blank=True, default=timezone.now)
    settingGST = models.ForeignKey(SettingGST, on_delete=models.CASCADE)

    def __unicode__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name).encode('ascii', 'replace')

    def all_order_product(self):
        order_products = OrderProducts.objects.filter(customer_order=self)
        if not order_products:
            return ""
        return format_html('<span>{}</span>', "".join(['({} - {} - {}{})'.format(
            op.product.product_name, op.product_size.size, op.weight, op.unit.name) for op in order_products]))


class OrderProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_size = models.ForeignKey(ProductSize, related_name='product', blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    customer_order = models.ForeignKey(CustomerOrder, on_delete=models.SET_NULL, null=True,
                                       related_name='customer_order')
    weight = models.FloatField(default=0)
    rate = models.FloatField(default=0)
    creation_date = models.DateTimeField('date created', auto_now_add=True)
    modified_date = models.DateTimeField('date last modified', auto_now=True)

    def __unicode__(self):
        return 'PRODUCT {} - {} {}'.format(self.product.product_name, self.weight, self.unit.name)


@receiver(post_save, sender=OrderProducts, dispatch_uid="update_tax_count")
def update_tax(sender, instance, **kwargs):
    print(instance.customer_order)
    print(instance.customer_order.id)
    print(instance.product)
    print(CustomerOrder.objects.get(pk=instance.customer_order.id))

    total = instance.customer_order.total
    setting_account = SettingAccount.objects.last()

    total += instance.weight * instance.rate

    discount = 0
    cgst = 0
    sgst = 0
    igst = 0
    if setting_account:
        if setting_account.setting_cgst and setting_account.setting_cgst > 0:
            cgst = (setting_account.setting_cgst * total) / 100

        if setting_account.setting_sgst and setting_account.setting_sgst > 0:
            sgst = (setting_account.setting_sgst * total) / 100

        if setting_account.setting_igst and setting_account.setting_igst > 0:
            igst = (setting_account.setting_igst * total) / 100

    net_amt = total + cgst + sgst + igst

    if setting_account and setting_account.discount and setting_account.discount > 0:
        discount = (setting_account.discount * net_amt) / 100

    grand_total = net_amt - discount

    instance.customer_order.cgst = cgst
    instance.customer_order.sgst = sgst
    instance.customer_order.igst = igst
    instance.customer_order.discount = discount + instance.customer_order.discount
    instance.customer_order.net_total = net_amt
    instance.customer_order.grand_total = grand_total
    instance.customer_order.total = total

    # make changes to model instance
    instance.customer_order.save()
    # instance.product.stock -= instance.amount
    # instance.product.save()
