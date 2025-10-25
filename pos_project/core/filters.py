from django_filters import rest_framework as filters
from .models import Articulo

class ArticuloFilter(filters.FilterSet):
    """
    Filtros personalizados para el ViewSet de Articulo.
    """
    # Filtro para buscar por texto 'que contenga' (icontains)
    descripcion = filters.CharFilter(field_name='descripcion', lookup_expr='icontains')

    # Filtros para buscar por ID exacto
    grupo = filters.UUIDFilter(field_name='grupo__grupo_id')
    linea = filters.UUIDFilter(field_name='linea__linea_id')

    class Meta:
        model = Articulo
        # Definimos los campos que creamos arriba
        fields = ['descripcion', 'grupo', 'linea']