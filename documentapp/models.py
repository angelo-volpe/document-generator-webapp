from typing import ClassVar

from django.db import models
from rest_framework import serializers


class Document(models.Model):
    name: ClassVar[models.CharField] = models.CharField(max_length=100)
    image: ClassVar[models.ImageField] = models.ImageField(upload_to="images/")

    def __str__(self) -> str:
        return self.name


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"


class Box(models.Model):
    document: ClassVar[models.ForeignKey] = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="box"
    )
    name: ClassVar[models.CharField] = models.CharField(max_length=100)
    is_alphabetic: ClassVar[models.BooleanField] = models.BooleanField(default=False)
    is_numeric: ClassVar[models.BooleanField] = models.BooleanField(default=False)
    mean_length: ClassVar[models.IntegerField] = models.IntegerField(default=0)
    start_x_norm: ClassVar[models.FloatField] = models.FloatField()
    start_y_norm: ClassVar[models.FloatField] = models.FloatField()
    end_x_norm: ClassVar[models.FloatField] = models.FloatField()
    end_y_norm: ClassVar[models.FloatField] = models.FloatField()

    def __str__(self) -> str:
        return f"Box for {self.document.name} with name: {self.name} at ({self.start_x_norm}, {self.start_y_norm}), ({self.end_x_norm}, {self.end_y_norm})"  # type: ignore[attr-defined]


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = "__all__"


class SampleDocument(models.Model):
    name: ClassVar[models.CharField] = models.CharField(max_length=100)
    image: ClassVar[models.ImageField] = models.ImageField(upload_to="document_samples/")
    template_document: ClassVar[models.ForeignKey] = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="samples"
    )

    def __str__(self) -> str:
        return self.name


class SampleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleDocument
        fields = "__all__"


class SampleBox(models.Model):
    sample_document: ClassVar[models.ForeignKey] = models.ForeignKey(
        SampleDocument, on_delete=models.CASCADE, related_name="sample_box"
    )
    template_box: ClassVar[models.ForeignKey] = models.ForeignKey(
        Box, on_delete=models.CASCADE, related_name="sample_box"
    )
    name: ClassVar[models.CharField] = models.CharField(max_length=100)
    label: ClassVar[models.CharField] = models.CharField(max_length=100)
    start_x_norm: ClassVar[models.FloatField] = models.FloatField()
    start_y_norm: ClassVar[models.FloatField] = models.FloatField()
    end_x_norm: ClassVar[models.FloatField] = models.FloatField()
    end_y_norm: ClassVar[models.FloatField] = models.FloatField()

    def __str__(self) -> str:
        return f"SampleBox for {self.sample_document.name} linked to template box {self.template_box.name}"  # type: ignore[attr-defined]


class SampleBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleBox
        fields = "__all__"
