from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import uuid
from django.contrib.auth import get_user_model
from django.db import transaction
from .filters import ArticuloFilter

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated  # <-- AÑADE ESTA
from .serializers import ArticuloSerializer, OrdenCompraClienteSerializer # <-- MODIFICA ESTA
from .models import Articulo # Esta ya debería estar, pero asegúrate

# Importaciones de Modelos
from core.models import (
    Articulo, GrupoArticulo, LineaArticulo, ListaPrecio,
    OrdenCompraCliente, ItemOrdenCompraCliente
)
# Importaciones de Forms
from core.forms import (
    ArticuloForm, ListaPrecioForm, OrdenForm, ItemOrdenForm
)
# Importaciones de Choices
from pos_project.choices import EstadoOrden

# --- IMPORTACIONES PARA DRF (API) ---
from rest_framework import viewsets
from .serializers import ArticuloSerializer


Usuario = get_user_model()

# ===============================================
# === VISTAS WEB (GUÍA 04) ===
# ===============================================

@login_required
def home(request):
    """Vista para la página principal (dashboard)."""
    total_articulos = Articulo.objects.count()
    total_usuarios = Usuario.objects.count()
    bajo_stock = Articulo.objects.filter(stock__lt=10).count()
    context = {
        'total_articulos': total_articulos,
        'total_usuarios': total_usuarios,
        'bajo_stock': bajo_stock,
        'ventas_hoy': 0, # Dato simulado
    }
    return render(request, 'core/index.html', context)

@login_required
def articulos_list(request):
    """Vista para listar artículos con paginación."""
    articulos_list = Articulo.objects.select_related('grupo', 'linea', 'listaprecio').all().order_by('descripcion')
    paginator = Paginator(articulos_list, 15) # 15 artículos por página
    page_number = request.GET.get('page')
    articulos = paginator.get_page(page_number)
    return render(request, 'core/articulos/list.html', {'articulos': articulos})

@login_required
def articulo_detail(request, articulo_id):
    """Vista para ver el detalle de un artículo."""
    articulo = get_object_or_404(Articulo, articulo_id=articulo_id)
    return render(request, 'core/articulos/detail.html', {'articulo': articulo})

@login_required
def articulo_create(request):
    """Vista para crear un nuevo artículo."""
    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        precio_form = ListaPrecioForm(request.POST)
        if form.is_valid() and precio_form.is_valid():
            articulo = form.save(commit=False)
            articulo.articulo_id = uuid.uuid4()
            articulo.save()
            
            lista_precio = precio_form.save(commit=False)
            lista_precio.articulo = articulo
            lista_precio.save()
            
            messages.success(request, 'Artículo creado correctamente.')
            return redirect('articulo_detail', articulo_id=articulo.articulo_id)
    else:
        form = ArticuloForm()
        precio_form = ListaPrecioForm()
    return render(request, 'core/articulos/form.html', {'form': form, 'precio_form': precio_form})

@login_required
def articulo_edit(request, articulo_id):
    """Vista para editar un artículo existente."""
    articulo = get_object_or_404(Articulo, articulo_id=articulo_id)
    lista_precio, created = ListaPrecio.objects.get_or_create(articulo=articulo)
    if request.method == 'POST':
        form = ArticuloForm(request.POST, instance=articulo)
        precio_form = ListaPrecioForm(request.POST, instance=lista_precio)
        if form.is_valid() and precio_form.is_valid():
            form.save()
            precio_form.save()
            messages.success(request, 'Artículo actualizado correctamente.')
            return redirect('articulo_detail', articulo_id=articulo.articulo_id)
    else:
        form = ArticuloForm(instance=articulo)
        precio_form = ListaPrecioForm(instance=lista_precio)
    return render(request, 'core/articulos/form.html', {'form': form, 'precio_form': precio_form})

@login_required
def articulo_delete(request, articulo_id):
    """Vista para eliminar un artículo."""
    articulo = get_object_or_404(Articulo, articulo_id=articulo_id)
    articulo.delete()
    messages.success(request, 'Artículo eliminado correctamente.')
    return redirect('articulos_list')


@login_required
def get_lineas_por_grupo(request, grupo_id):
    """API simple para obtener líneas de artículo para AJAX."""
    lineas = LineaArticulo.objects.filter(grupo_id=grupo_id, estado=1).values('linea_id', 'nombre_linea')
    return JsonResponse(list(lineas), safe=False)

def cargar_lineas(request):
    grupo_id = request.GET.get('grupo_id')
    lineas = LineaArticulo.objects.filter(grupo_id=grupo_id, estado=1).order_by('nombre_linea')  # 1 = ACTIVO
    data = [{'id': linea.pk, 'nombre': linea.nombre_linea} for linea in lineas]
    return JsonResponse(data, safe=False)

# ===============================================
# === VISTAS DEL CARRITO DE COMPRAS (GUÍA 05) ===
# ===============================================

@login_required
def crear_orden(request):
    """
    Crea una nueva orden de compra para el cliente actual o recupera la existente.
    """
    orden, created = OrdenCompraCliente.objects.get_or_create(
        cliente=request.user,
        estado=EstadoOrden.PENDIENTE
    )
    
    if created:
        orden.save()
        messages.success(request, 'Nuevo carrito de compras creado.')
    else:
        messages.info(request, 'Tienes un carrito de compras pendiente.')

    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    """
    Muestra el carrito de compras (orden pendiente) del usuario.
    """
    try:
        orden = OrdenCompraCliente.objects.get(cliente=request.user, estado=EstadoOrden.PENDIENTE)
        items = orden.items.all().order_by('articulo__descripcion')
        
        orden.importe = sum(item.total_item for item in items)
        orden.save()

    except OrdenCompraCliente.DoesNotExist:
        orden = None
        items = []
        messages.warning(request, 'No tienes un carrito de compras activo.')

    return render(request, 'core/ordenes/ver_carrito.html', {
        'orden': orden,
        'items': items
    })

@login_required
@transaction.atomic 
def agregar_al_carrito(request, articulo_id):
    """
    Agrega un artículo al carrito de compras (orden pendiente).
    """
    articulo = get_object_or_404(Articulo, articulo_id=articulo_id)
    
    orden, created = OrdenCompraCliente.objects.get_or_create(
        cliente=request.user,
        estado=EstadoOrden.PENDIENTE
    )
    
    precio = getattr(articulo.listaprecio, 'precio_1', 0)
    if precio <= 0:
        messages.error(request, f"El artículo '{articulo.descripcion}' no tiene precio definido.")
        return redirect(request.META.get('HTTP_REFERER', 'articulos_list'))

    item, item_created = ItemOrdenCompraCliente.objects.get_or_create(
        orden=orden,
        articulo=articulo,
        defaults={
            'cantidad': 1,
            'precio_unitario': precio
        }
    )
    
    if not item_created:
        item.cantidad += 1
        item.save()
        messages.success(request, f"Se agregó otra unidad de '{articulo.descripcion}' al carrito.")
    else:
        messages.success(request, f"'{articulo.descripcion}' agregado al carrito.")

    return redirect(request.META.get('HTTP_REFERER', 'articulos_list'))

@login_required
@transaction.atomic
def eliminar_del_carrito(request, item_id):
    """
    Elimina un ítem específico del carrito de compras.
    """
    item = get_object_or_404(ItemOrdenCompraCliente, item_id=item_id, orden__cliente=request.user)
    
    if item.orden.estado == EstadoOrden.PENDIENTE:
        descripcion_articulo = item.articulo.descripcion
        item.delete()
        messages.info(request, f"'{descripcion_articulo}' fue eliminado del carrito.")
    else:
        messages.error(request, "No se puede eliminar un ítem de una orden que no está pendiente.")
        
    return redirect('ver_carrito')

@login_required
@transaction.atomic
def confirmar_orden(request):
    """
    Confirma la orden pendiente, cambia su estado a 'Procesando'.
    """
    try:
        orden = OrdenCompraCliente.objects.get(cliente=request.user, estado=EstadoOrden.PENDIENTE)
        items = orden.items.all()
        
        if not items.exists():
            messages.error(request, "Tu carrito está vacío, no se puede confirmar.")
            return redirect('ver_carrito')
            
        orden.importe = sum(item.total_item for item in items)
        orden.estado = EstadoOrden.PROCESANDO
        orden.save()
        
        messages.success(request, f"Orden #{orden.pedido_id} confirmada exitosamente.")
        return redirect('orden_confirmada', orden_id=orden.pedido_id)

    except OrdenCompraCliente.DoesNotExist:
        messages.error(request, "No tienes una orden pendiente para confirmar.")
        return redirect('home')

@login_required
def orden_confirmada(request, orden_id):
    """
    Muestra la página de "gracias" después de confirmar la orden.
    """
    orden = get_object_or_404(OrdenCompraCliente, pedido_id=orden_id, cliente=request.user)
    return render(request, 'core/ordenes/orden_confirmada.html', {'orden': orden})

@login_required
def mis_ordenes(request):
    """
    Muestra el historial de órdenes del cliente.
    """
    ordenes = OrdenCompraCliente.objects.filter(cliente=request.user).exclude(estado=EstadoOrden.PENDIENTE).order_by('-fecha_pedido')
    return render(request, 'core/ordenes/mis_ordenes.html', {'ordenes': ordenes})

@login_required
def detalle_orden(request, orden_id):
    """
    Muestra el detalle de una orden específica (confirmada o pasada).
    """
    orden = get_object_or_404(OrdenCompraCliente, pedido_id=orden_id, cliente=request.user)
    items = orden.items.all().order_by('articulo__descripcion')
    
    return render(request, 'core/ordenes/detalle_orden.html', {
        'orden': orden,
        'items': items
    })

# ===============================================
# === VISTAS DE API (DRF CON VIEWSETS - GUÍA 06) ===
# ===============================================

class ArticuloViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver, crear, actualizar y eliminar Artículos.
    Combina todas las operaciones (List, Retrieve, Create, Update, Delete)
    en una sola clase.
    """
    queryset = Articulo.objects.select_related('grupo', 'linea', 'listaprecio').all().order_by('descripcion')
    serializer_class = ArticuloSerializer
    lookup_field = 'articulo_id' # Le seguimos diciendo que use 'articulo_id'

    filterset_class = ArticuloFilter
    # ... (debajo de ArticuloViewSet)

class OrdenViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite a los usuarios ver sus propias órdenes.
    Es de "Solo Lectura" (no se pueden crear/borrar órdenes desde aquí).
    """
    serializer_class = OrdenCompraClienteSerializer
    permission_classes = [IsAuthenticated] # <-- Solo usuarios logueados pueden ver esto
    lookup_field = 'pedido_id'

    def get_queryset(self):
        """
        Sobrescribimos este método para que la API solo devuelva
        las órdenes que pertenecen al usuario que está haciendo la consulta.
        """
        return OrdenCompraCliente.objects.filter(cliente=self.request.user).order_by('-fecha_pedido')