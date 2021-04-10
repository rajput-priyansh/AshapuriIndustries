from __future__ import unicode_literals
from django.db import models

from django.contrib.auth.models import User

# Create your models here.
from django.utils.encoding import smart_str


class Account(models.Model):
    QUESTION_ACTOR = 'actor'
    QUESTION_COLOR = 'color'
    QUESTION_PET = 'pet'
    QUESTION_SINGER = 'singer'

    QUESTION_CHOICES = (
        (QUESTION_ACTOR, 'Who is your favorite actor/actress?'),
        (QUESTION_COLOR, 'What is your favorite color?'),
        (QUESTION_PET, 'What is the name of your pet?'),
        (QUESTION_SINGER, 'Who is your favorite singer?'),
    )
    full_name = models.CharField(max_length=300, blank=False, null=False)
    email = models.EmailField(max_length=254, blank=True, null=True)
    mobile_number = models.CharField(max_length=12, blank=True, null=True, default="")
    other_mobile_number = models.CharField(max_length=12, blank=False, null=False)
    image = models.ImageField(upload_to='', blank=True, null=True)
    is_approved = models.BooleanField(default=True, help_text='Used for approving user registration.')
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    State = models.CharField(max_length=50, blank=True)
    creation_date = models.DateTimeField('date created', auto_now_add=True)
    modified_date = models.DateTimeField('date last modified', auto_now=True)
    is_active = models.BooleanField(default=True, help_text='Used for Active/Inactive customer.')
    pan_number = models.CharField(max_length=50, blank=True, help_text='PAN CARD number')
    gst_number = models.CharField(max_length=100, blank=True, help_text='GST number')
    is_favourite = models.BooleanField(default=False, help_text='Used for add users as favourite.')

    def __unicode__(self):
        return "{}".format(self.full_name).encode('ascii', 'replace')

    def __str__(self):
        return smart_str("{}".format(self.full_name).encode('ascii', 'replace'))

    @property
    def get_full_name(self):
        return "{}".format(self.full_name).encode('ascii', 'replace')


class SettingAccount(models.Model):
    discount = models.FloatField(help_text='DISCOUNT IN PERCENTAGE (0 to 100).', max_length=3)
    bank_name = models.CharField(max_length=250, blank=True, help_text='Bank full name')
    account_number = models.CharField(max_length=25, blank=True, help_text='Bank Account number')
    bank_address = models.CharField(max_length=25, blank=True, help_text='Bank Address')
    bank_ifsc = models.CharField(max_length=25, blank=True, help_text='Bank IFSC Code')
    pan_number = models.CharField(max_length=50, blank=True, help_text='PAN CARD number')
    gst_number = models.CharField(max_length=100, blank=True, help_text='GST number')
    mobile_number = models.CharField(max_length=12, blank=False, null=False)
    state = models.CharField(max_length=50, help_text="State Name", default="Gujrat")
    state_code = models.CharField(max_length=10, help_text="State Code", default="24")
    supply_address = models.CharField(max_length=250, help_text="Place Of Supply", default="Makarpura")

    def __unicode__(self):
        return str(self.discount).encode('ascii', 'replace')

    def __str__(self):
        return smart_str(str(self.discount).encode('ascii', 'replace'))


class SettingGST(models.Model):
    setting_cgst = models.FloatField(max_length=3, default=0, help_text='CGST IN PERCENTAGE (0 to 100).')
    setting_sgst = models.FloatField(max_length=3, default=0, help_text='SGST IN PERCENTAGE (0 to 100).')
    setting_igst = models.FloatField(max_length=3, default=0, help_text='IGST IN PERCENTAGE (0 to 100).')

    def __unicode__(self):
        return "CGST:{}, SGST:{}, IGST:{}".format(self.setting_cgst, self.setting_sgst, self.setting_igst).encode('ascii', 'replace')

    def __str__(self):
        return smart_str("CGST:{}, SGST:{}, IGST:{}".format(self.setting_cgst, self.setting_sgst, self.setting_igst).encode(
            'ascii', 'replace'))


class TermsConditions(models.Model):
    term_condition = models.CharField(max_length=400, blank=True, help_text='Term & Condition')

    def __unicode__(self):
        return str(self.term_condition).encode('ascii', 'replace')

    def __str__(self):
        return smart_str(str(self.term_condition).encode('ascii', 'replace'))


