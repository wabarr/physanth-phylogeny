from django.db import models

class AdType(models.Model):
    description = models.CharField(max_length=150)
    vendor = models.CharField(max_length=100, default="Amazon")
    def __unicode__(self):
        return self.description + "-" + self.vendor

class Ad(models.Model):
    product_name = models.CharField(max_length=150, null=True, blank=True)
    type = models.ForeignKey(AdType)
    html = models.CharField(max_length = 1000)
    def __unicode__(self):
        return self.product_name + "-" + self.type.description


