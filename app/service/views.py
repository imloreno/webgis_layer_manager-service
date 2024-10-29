import tempfile, os, json

from django.contrib.gis.geos import GEOSGeometry
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, viewsets, decorators

from .models import Layer, Feature
from .serializers import LayerSerializer


class GeoJsonViewSet(viewsets.ModelViewSet):
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        # Check if the file is present
        if 'layer_file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Setting the default values for the Layer model
        geojson_file = request.FILES['layer_file']
        sorting = request.data.get('sorting')
        coordinate_system = request.data.get('coordinate_system', 'unknown')
        layer_name = request.data.get('layer_name', 'Unknown')

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            for chunk in geojson_file.chunks():
                temp_file.write(chunk)
            temp_file.close()

            with open(temp_file.name, 'r') as f:
                geojson_data = json.load(f)

             # Check if the file is a valid GeoJSON file, if not return an error
            if geojson_data.get("type") != "FeatureCollection":
                return Response({"error": "Invalid GeoJSON file"}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new Layer object
            layer = Layer.objects.create(layer_name=layer_name, sorting=sorting, original_file=geojson_file, coordinate_system=coordinate_system)

            # Create Feature objects for each feature in the FeatureCollection
            features = geojson_data.get("features", [])
            for feature in features:
                # Extract the geometry field, if geometry is not present, try with location, if not present, set it to an empty dictionary
                geometry = feature.get("geometry", feature.get("location", {}))
                properties = feature.get("properties", {})

                try:
                    geometry_obj = GEOSGeometry(json.dumps(geometry), srid=4326)
                    Feature.objects.create(
                        fk_layers=layer,
                        type=geometry.get("type", "Unknown"),
                        properties=properties,
                        geometry=geometry_obj
                    )
                except Exception as e:
                    print(f"Error creating Feature from layer {layer_name}: {e}")
                    return Response({"Error retrieving Feature's fields.": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(LayerSerializer(layer).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error creating Layer: {e}")
            return Response({"Error creating Layer": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            os.unlink(temp_file.name)

    @decorators.action(detail=True, methods=['get'])
    def geojson(self, request, *args, **kwargs):
        layer = self.get_object()
        features = layer.features.filter(fk_layers=layer)

        geojson = {
            "type": "FeatureCollection",
            "name": layer.layer_name,
            "crs": {
                "type": "name",
                "properties": {
                    "name": layer.coordinate_system
                }
            },
            "features": []
        }

        for feature in features:
            geojson_feature = {
                "type": "Feature",
                "properties": feature.properties,
                "geometry": json.loads(feature.geometry.geojson) if feature.geometry else {}
            }
            geojson["features"].append(geojson_feature)

        return Response(geojson, status=status.HTTP_200_OK)