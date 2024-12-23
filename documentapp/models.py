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
        fields = "__all__"


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


class SampleDocument(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="document_samples/")
    template_document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="samples")

    def __str__(self):
        return self.name
    

class SampleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleDocument
        fields = "__all__"
    

class SampleBox(models.Model):
    sample_document = models.ForeignKey(SampleDocument, on_delete=models.CASCADE, related_name='sample_box')
    template_box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='sample_box')
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    start_x_norm = models.FloatField()
    start_y_norm = models.FloatField()
    end_x_norm = models.FloatField()
    end_y_norm = models.FloatField()


class SampleBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleBox
        fields = '__all__'
