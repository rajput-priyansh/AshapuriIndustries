from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.html import format_html
from account.models import Account, SettingAccount, SettingGST

from django.db.models.signals import post_save
from django.dispatch import receiver


class BagWightUnit(models.Model):
    display_name = models.CharField(max_length=50, null=False, blank=False, help_text="Unit name e.i. (50KG), (25GM)")
    unit = models.CharField(max_length=50,  default="", help_text="Unit e.i. KG, GM")
    wight = models.FloatField(default=0, help_text="Unit Wight e.i. 50, 25")
    description = models.TextField(null=True, blank=True, help_text="Write about the unit")

    def __unicode__(self):
        return self.display_name.encode('ascii', 'replace')

    def __str__(self):
        return smart_str(self.display_name)


class Product(models.Model):
    product_name = models.CharField(max_length=100, blank=False, null=False, help_text="Product simple Name")
    product_type = models.CharField(max_length=50, help_text="Product Type")
    hsn_number = models.CharField(max_length=10, blank=True, null=True, help_text='HSN/ACS number')

    def __unicode__(self):
        return self.product_name.encode('ascii', 'replace')

    def __str__(self):
        return smart_str(self.product_name)


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
    transportation_mode = models.CharField(max_length=50, help_text="Transportation Mode", default="")
    vehicle_number = models.CharField(max_length=50, help_text="Vehicle Number", default="")
    order_number = models.CharField(max_length=100, help_text="Order number", blank=True, null=True)
    invoice_date = models.DateTimeField('invoice date', blank=True, default=timezone.now)
    settingGST = models.ForeignKey(SettingGST, on_delete=models.CASCADE)

    def __unicode__(self):
        return "{}".format(self.user.full_name).encode('ascii', 'replace')

    def __str__(self):
        return smart_str("{}".format(self.user.full_name).encode('ascii', 'replace'))

    def all_order_product(self):
        order_products = OrderProducts.objects.filter(customer_order=self)
        if not order_products:
            return ""
        return format_html('<span>{}</span>', "".join(['({} - {} - {}{})'.format(
            op.product.product_name, op.no_of_bag, (op.no_of_bag * op.bag_wight_unit.wight), op.bag_wight_unit.display_name) for op in order_products]))


class OrderProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    no_of_bag = models.IntegerField(default=0, help_text="Product Bag number e.i Bag, Box, Box karton")
    bag_wight_unit = models.ForeignKey(BagWightUnit, on_delete=models.CASCADE)
    customer_order = models.ForeignKey(CustomerOrder, on_delete=models.SET_NULL, null=True,
                                       related_name='customer_order')
    rate = models.FloatField(default=0)
    creation_date = models.DateTimeField('date created', auto_now_add=True)
    modified_date = models.DateTimeField('date last modified', auto_now=True)

    def __unicode__(self):
        return 'PRODUCT {} - {} {}'.format(self.product.product_name,
                                           (self.bag_wight_unit.wight * self.no_of_bag),
                                           self.bag_wight_unit.display_name)

    def __str__(self):
        return smart_str('PRODUCT {} - {} {}'.format(self.product.product_name,
                                           (self.bag_wight_unit.wight * self.no_of_bag),
                                           self.bag_wight_unit.display_name))


@receiver(post_save, sender=OrderProducts, dispatch_uid="update_tax_count")
def update_tax(sender, instance, **kwargs):
    print(instance.customer_order)
    print(instance.customer_order.id)
    print(instance.product)
    print(CustomerOrder.objects.get(pk=instance.customer_order.id))

    total = instance.customer_order.total
    setting_account = SettingAccount.objects.last()
    setting_GST = instance.customer_order.settingGST

    total += (instance.bag_wight_unit.wight * instance.no_of_bag) * instance.rate

    discount = 0
    cgst = 0
    sgst = 0
    igst = 0
    if setting_GST:
        if setting_GST.setting_cgst and setting_GST.setting_cgst > 0:
            cgst = (setting_GST.setting_cgst * total) / 100

        if setting_GST.setting_sgst and setting_GST.setting_sgst > 0:
            sgst = (setting_GST.setting_sgst * total) / 100

        if setting_GST.setting_igst and setting_GST.setting_igst > 0:
            igst = (setting_GST.setting_igst * total) / 100

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
