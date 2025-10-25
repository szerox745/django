from rest_framework import serializers
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
    Serializer dinámico:
    - LECTURA: Muestra todos los objetos anidados (Grupo, Linea, ListaPrecio).
    - ESCRITURA: Solo pide los IDs (UUIDs) de grupo y linea.
    """
    
    # --- CAMPOS ANIDADOS (SOLO LECTURA) ---
    grupo = GrupoArticuloSerializer(read_only=True)
    linea = LineaArticuloSerializer(read_only=True)
    listaprecio = ListaPrecioSerializer(read_only=True)

    # --- CAMPOS PARA ESCRITURA (CREAR/ACTUALIZAR) ---
    grupo_id = serializers.UUIDField(source='grupo', write_only=True)
    linea_id = serializers.UUIDField(source='linea', write_only=True)
    
    class Meta:
        model = Articulo
        fields = [
            'articulo_id',
            'codigo_articulo',
            'descripcion',
            'stock',
            
            # Campos de lectura (anidados)
            'grupo',
            'linea',
            'listaprecio',
            
            # Campos de escritura (IDs)
            'grupo_id',
            'linea_id'
        ]
        
        read_only_fields = ['articulo_id', 'grupo', 'linea', 'listaprecio']
        write_only_fields = ['grupo_id', 'linea_id']

    def validate_stock(self, value):
        """
        Validación a nivel de campo: Asegura que el stock no sea negativo.
        """
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate(self, data):
        """
        Validación a nivel de objeto: Comprueba dependencias (ej: que la línea pertenezca al grupo).
        """
        if 'grupo' in data and 'linea' in data:
            grupo = data['grupo']
            linea = data['linea']
            
            if not hasattr(linea, 'grupo'):
                raise serializers.ValidationError("Línea no encontrada.")

            if linea.grupo != grupo:
                raise serializers.ValidationError(
                    f"La línea '{linea.nombre_linea}' no pertenece al grupo '{grupo.nombre_grupo}'."
                )
        return data

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
    cliente = UsuarioSerializer(read_only=True)
    items = ItemOrdenCompraClienteSerializer(many=True, read_only=True)
    estado = serializers.CharField(source='get_estado_display')

    class Meta:
        model = OrdenCompraCliente
        fields = [
            'pedido_id',
            'cliente',
            'fecha_pedido',
            'importe',
            'estado',
            'items'
        ]