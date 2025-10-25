from django.contrib import admin
from .models import (
    GrupoArticulo, 
    LineaArticulo, 
    Articulo, 
    ListaPrecio,
    OrdenCompraCliente,
    ItemOrdenCompraCliente
)

# Registra tus modelos aquí.
admin.site.register(GrupoArticulo)
admin.site.register(LineaArticulo)
admin.site.register(Articulo)
admin.site.register(ListaPrecio)
admin.site.register(OrdenCompraCliente)
admin.site.register(ItemOrdenCompraCliente)