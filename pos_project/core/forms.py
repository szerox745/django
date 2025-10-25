from django import forms
from .models import Articulo, ListaPrecio, GrupoArticulo, LineaArticulo, OrdenCompraCliente, ItemOrdenCompraCliente
from pos_project.choices import EstadoEntidades

class ArticuloForm(forms.ModelForm):
    """
    Formulario para el modelo Articulo.
    """
    class Meta:
        model = Articulo
        fields = [
            'codigo_articulo', 
            'codigo_barras', 
            'descripcion',
            'presentacion',
            'grupo', 
            'linea', 
            'stock'
        ]
        widgets = {
            'codigo_articulo': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'presentacion': forms.TextInput(attrs={'class': 'form-control'}),
            'grupo': forms.Select(attrs={'class': 'form-select'}),
            'linea': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Sobrescribimos el __init__ para manejar la lógica de los dropdowns dependientes (Grupo -> Línea).
        """
        super().__init__(*args, **kwargs)

        # 1. El queryset del campo 'grupo' siempre mostrará solo los grupos activos.
        self.fields['grupo'].queryset = GrupoArticulo.objects.filter(estado=EstadoEntidades.ACTIVO)

        # 2. Por defecto, el queryset del campo 'linea' empieza vacío.
        #    Esto evita el error al crear un nuevo artículo, ya que no hay un grupo seleccionado.
        self.fields['linea'].queryset = LineaArticulo.objects.none()

        # 3. Si el formulario se está enviando (POST), filtramos las líneas según el grupo enviado.
        if 'grupo' in self.data:
            try:
                grupo_id = self.data.get('grupo')
                # Importante: No convertir a int para evitar errores con UUID o strings
                self.fields['linea'].queryset = LineaArticulo.objects.filter(
                    grupo_id=grupo_id,
                    estado=EstadoEntidades.ACTIVO
                ).order_by('nombre_linea')
            except (ValueError, TypeError):
                pass  # Si el valor no es válido, la validación del formulario se encargará.

        # 4. Si estamos editando un artículo existente (GET), filtramos las líneas según el grupo guardado.
        elif self.instance.pk and getattr(self.instance, 'grupo', None):
            self.fields['linea'].queryset = self.instance.grupo.lineas.filter(
                estado=EstadoEntidades.ACTIVO
            ).order_by('nombre_linea')


class ListaPrecioForm(forms.ModelForm):
    """
    Formulario para el modelo ListaPrecio.
    """
    class Meta:
        model = ListaPrecio
        fields = [
            'precio_1', 
            'precio_2', 
            'precio_3', 
            'precio_4',
            'precio_compra', 
            'precio_costo'
        ]
        widgets = {
            'precio_1': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'precio_2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'precio_3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'precio_4': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


class OrdenForm(forms.ModelForm):
    class Meta:
        model = OrdenCompraCliente
        fields = ['cliente', 'estado'] # Campos iniciales

class ItemOrdenForm(forms.ModelForm):
    class Meta:
        model = ItemOrdenCompraCliente
        fields = ['articulo', 'cantidad', 'precio_unitario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['articulo'].queryset = Articulo.objects.filter(estado=EstadoEntidades.ACTIVO)