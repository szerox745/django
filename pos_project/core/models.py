import uuid
from django.db import models
from pos_project.choices import EstadoEntidades, EstadoOrden
from django.contrib.auth import get_user_model

# Modelo para agrupar artículos (ej: Bebidas, Lácteos, Limpieza)
class GrupoArticulo(models.Model):
    grupo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_grupo = models.CharField(max_length=150)
    estado = models.IntegerField(choices=EstadoEntidades.choices, default=EstadoEntidades.ACTIVO)

    def __str__(self):
        return self.nombre_grupo

    class Meta:
        db_table = "grupos_articulos"
        verbose_name = "Grupo de Artículo"
        verbose_name_plural = "Grupos de Artículos"

# Modelo para una sub-categoría dentro de un Grupo (ej: Gaseosas, Jugos)
class LineaArticulo(models.Model):
    linea_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.CASCADE, related_name='lineas')
    nombre_linea = models.CharField(max_length=150)
    estado = models.IntegerField(choices=EstadoEntidades.choices, default=EstadoEntidades.ACTIVO)

    def __str__(self):
        return self.nombre_linea

    class Meta:
        db_table = "lineas_articulos"
        verbose_name = "Línea de Artículo"
        verbose_name_plural = "Líneas de Artículos"

# Modelo principal para los artículos o productos
class Articulo(models.Model):
    articulo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_articulo = models.CharField(max_length=25, unique=True)
    codigo_barras = models.CharField(max_length=25, null=True, blank=True)
    descripcion = models.CharField(max_length=150)
    presentacion = models.CharField(max_length=100, null=True, blank=True)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.PROTECT)
    linea = models.ForeignKey(LineaArticulo, on_delete=models.PROTECT)
    stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.IntegerField(choices=EstadoEntidades.choices, default=EstadoEntidades.ACTIVO)

    def __str__(self):
        return self.descripcion

    class Meta:
        db_table = "articulos"
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"

# Modelo para almacenar los diferentes precios de un artículo
class ListaPrecio(models.Model):
    articulo = models.OneToOneField(Articulo, on_delete=models.CASCADE, primary_key=True, related_name='listaprecio')
    precio_1 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_2 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_3 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_4 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_costo = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Precios de {self.articulo.descripcion}"

    class Meta:
        db_table = "lista_precios"
        verbose_name = "Lista de Precio"
        verbose_name_plural = "Listas de Precios"

# --- AGREGA ESTOS MODELOS AL FINAL ---

class OrdenCompraCliente(models.Model):
    pedido_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    importe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.IntegerField(choices=EstadoOrden.choices, default=EstadoOrden.PENDIENTE)

    def __str__(self):
        return f"Orden {self.pedido_id} - Cliente {self.cliente.full_name}"

    class Meta:
        db_table = "ordenes_compra_cliente"
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"

class ItemOrdenCompraCliente(models.Model):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey(OrdenCompraCliente, on_delete=models.CASCADE, related_name='items')
    articulo = models.ForeignKey(Articulo, on_delete=models.RESTRICT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    total_item = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calcula el total del item antes de guardar
        self.total_item = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.articulo.descripcion} - Orden {self.orden.pedido_id}"

    class Meta:
        db_table = "items_orden_compra_cliente"
        verbose_name = "Ítem de Orden"
        verbose_name_plural = "Ítems de Órdenes"

