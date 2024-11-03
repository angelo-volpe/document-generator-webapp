from django.db import models
from rest_framework import serializers


class Document(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name


class BoxCoordinate(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='box_coordinates')
    name = models.CharField(max_length=100)
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()

    def __str__(self):
        return f"Box for {self.document.name} with name: {self.name} at ({self.x1}, {self.y1}), ({self.x2}, {self.y2})"
    

class BoxCoordinateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxCoordinate
        fields = '__all__'