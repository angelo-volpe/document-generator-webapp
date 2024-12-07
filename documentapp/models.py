from django.db import models
from rest_framework import serializers


class Document(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'image']


class Box(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='box')
    name = models.CharField(max_length=100)
    is_alphabetic = models.BooleanField(default=False)
    is_numeric = models.BooleanField(default=False)
    mean_length = models.IntegerField(default=0)
    start_x_norm = models.FloatField()
    start_y_norm = models.FloatField()
    end_x_norm = models.FloatField()
    end_y_norm = models.FloatField()

    def __str__(self):
        return f"Box for {self.document.name} with name: {self.name} at ({self.start_x}, {self.start_y}), ({self.end_x}, {self.end_y})"
    

class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = '__all__'