from django.db import models


class POD(models.Model):
    sr_no = models.IntegerField()
    employee_code = models.CharField(max_length=20)
    employee_name = models.CharField(max_length=100)
    to_be_sent_to_e_name = models.CharField(max_length=100)
    secretary_code = models.CharField(max_length=20)
    address = models.TextField()
    mobile_no = models.CharField(max_length=15)
    pod_number = models.CharField(max_length=20)
    desp_on = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    pod_image = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.pod_number
