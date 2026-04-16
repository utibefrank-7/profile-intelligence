from django.db import models

# Create your models here.
class Profile(models.Model):
    id =models.CharField(max_length=36,primary_key=True, editable=False)
    name =models.CharField(max_length=100, unique=True)
    gender =models.CharField(max_length=50, null=True, blank=True)
    gender_probability =models.FloatField(null=True, blank=True)
    sample_size =models.IntegerField(null=True, blank=True)
    age =models.IntegerField(null=True, blank=True)
    age_group =models.CharField(max_length=50, null=True, blank=True)
    country_id =models.CharField(max_length=10, null=True, blank=True)
    country_probability =models.FloatField(null=True, blank=True)
    created_at =models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table ="profiles"
    
