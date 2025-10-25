from rest_framework import serializers
# --- MODIFICA ESTA LÍNEA ---
from .models import (
    Articulo, ListaPrecio, GrupoArticulo, LineaArticulo,
    OrdenCompraCliente, ItemOrdenCompraCliente
)
from django.contrib.auth import get_user_model

class GrupoArticuloSerializer(serializers.ModelSerializer):
    """ Serializer para el modelo GrupoArticulo """
    class Meta:
        model = GrupoArticulo
        fields = ['grupo_id', 'nombre_grupo']

class LineaArticuloSerializer(serializers.ModelSerializer):
    """ Serializer para el modelo LineaArticulo """
    class Meta:
        model = LineaArticulo
        fields = ['linea_id', 'nombre_linea']

class ListaPrecioSerializer(serializers.ModelSerializer):
    """ Serializer para el modelo ListaPrecio """
    class Meta:
        model = ListaPrecio
        fields = ['precio_1', 'precio_2', 'precio_compra', 'precio_costo']

class ArticuloSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Articulo.
    Incluye serializadores anidados para Grupo, Linea y ListaPrecio.
    """
    # Usamos los serializers anidados que definimos arriba
    grupo = GrupoArticuloSerializer(read_only=True)
    linea = LineaArticuloSerializer(read_only=True)
    listaprecio = ListaPrecioSerializer(read_only=True)

    # Campos que queremos exponer del modelo Articulo
    class Meta:
        model = Articulo
        fields = [
            'articulo_id',
            'codigo_articulo',
            'descripcion',
            'stock',
            'grupo',
            'linea',
            'listaprecio'
        ]

# ===============================================
# === SERIALIZERS PARA ÓRDENES (GUÍA 06) ===
# ===============================================

class UsuarioSerializer(serializers.ModelSerializer):
    """ Serializer simple para mostrar info del Usuario """
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'full_name', 'email']


class ArticuloSimpleSerializer(serializers.ModelSerializer):
    """ Un serializer más simple para Articulo, usado dentro de los items de la orden """
    class Meta:
        model = Articulo
        fields = ['articulo_id', 'descripcion', 'codigo_articulo']


class ItemOrdenCompraClienteSerializer(serializers.ModelSerializer):
    """ Serializer para el modelo ItemOrdenCompraCliente (el detalle de la orden) """
    # Usamos el serializer simple de Artículo para no anidar toda la info
    articulo = ArticuloSimpleSerializer(read_only=True)

    class Meta:
        model = ItemOrdenCompraCliente
        fields = [
            'item_id',
            'articulo',
            'cantidad',
            'precio_unitario',
            'total_item'
        ]


class OrdenCompraClienteSerializer(serializers.ModelSerializer):
    """ Serializer para el modelo OrdenCompraCliente (la cabecera de la orden) """

    # Anidamos el serializer de Usuario
    cliente = UsuarioSerializer(read_only=True)

    # Anidamos los Items (detalle) de la orden.
    # 'many=True' porque una orden tiene muchos items.
    items = ItemOrdenCompraClienteSerializer(many=True, read_only=True)

    # Añadimos un campo 'get_estado_display' para ver el texto del estado
    estado = serializers.CharField(source='get_estado_display')

    class Meta:
        model = OrdenCompraCliente
        fields = [
            'pedido_id',
            'cliente',
            'fecha_pedido',
            'importe',
            'estado',
            'items' # <--- El detalle anidado
        ]