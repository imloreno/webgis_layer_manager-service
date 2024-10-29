import uuid
from django.contrib.gis.db import models

class Layer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sorting = models.IntegerField()  # Sorting order
    layer_name = models.CharField(max_length=255)  # Name of the layer
    original_file = models.FileField(upload_to='media/layers/files/')  # Stores the uploaded file
    coordinate_system = models.CharField(max_length=200)  # Coordinate system used

    def __str__(self):
        return self.layer_name


class Feature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fk_layers = models.ForeignKey(Layer, related_name='features', on_delete=models.CASCADE)  # Foreign key relationship to Layer
    type = models.CharField(max_length=50)  # Type of feature (e.g., Point, LineString, Polygon)
    properties = models.JSONField()  # Properties of the feature
    geometry = models.GeometryField(srid=4326, null=True, blank=True)  # Stores geometry of the feature

    def __str__(self):
        return f"Feature {self.id} of Layer {self.fk_layers.layer_name}"
