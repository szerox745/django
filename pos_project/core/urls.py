from django.urls import path
from . import views

urlpatterns = [
    # --- URLs DE ARTÍCULOS (Ya las tenías) ---
    path('articulos/', views.articulos_list, name='articulos_list'),
    path('articulos/nuevo/', views.articulo_create, name='articulo_create'),
    path('articulos/<uuid:articulo_id>/', views.articulo_detail, name='articulo_detail'),
    path('articulos/<uuid:articulo_id>/editar/', views.articulo_edit, name='articulo_edit'),
    path('articulos/<uuid:articulo_id>/eliminar/', views.articulo_delete, name='articulo_delete'),
    
    # --- URLs DE AJAX (Ya las tenías) ---
    path('api/lineas-por-grupo/<uuid:grupo_id>/', views.get_lineas_por_grupo, name='get_lineas_por_grupo'),
    path('ajax/cargar-lineas/', views.cargar_lineas, name='ajax_cargar_lineas'),

    # --- NUEVAS URLs DEL CARRITO Y ÓRDENES ---
    path('carrito/crear/', views.crear_orden, name='crear_orden'),
    path('carrito/ver/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<uuid:articulo_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<uuid:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/confirmar/', views.confirmar_orden, name='confirmar_orden'),
    
    path('orden/confirmada/<uuid:orden_id>/', views.orden_confirmada, name='orden_confirmada'),
    path('orden/detalle/<uuid:orden_id>/', views.detalle_orden, name='detalle_orden'),
    path('ordenes/mis-ordenes/', views.mis_ordenes, name='mis_ordenes'),
]