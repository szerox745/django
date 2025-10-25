import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import GrupoArticulo, LineaArticulo, Articulo, ListaPrecio

class Command(BaseCommand):
    help = 'Importa datos desde archivos CSV a la base de datos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Iniciando importación de datos ---'))

        # Ruta base donde están los CSV (junto a manage.py)
        base_dir = settings.BASE_DIR

        # --- 1. IMPORTAR GRUPOS ---
        self.stdout.write('Importando Grupos de Artículos...')
        ruta_grupos = os.path.join(base_dir, 'grupos_articulos.csv')
        
        try:
            with open(ruta_grupos, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    GrupoArticulo.objects.get_or_create(
                        grupo_id=row['grupo_id'],
                        defaults={
                            'nombre_grupo': row['nombre_grupo'],
                            'estado': row['estado']
                        }
                    )
            self.stdout.write(self.style.SUCCESS(f"✔ Grupos importados desde {ruta_grupos}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importando grupos: {e}"))
            return

        # --- 2. IMPORTAR LÍNEAS ---
        self.stdout.write('Importando Líneas de Artículos...')
        ruta_lineas = os.path.join(base_dir, 'catalogo_lineas_proyecto_uss.csv')

        try:
            with open(ruta_lineas, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Buscamos el grupo al que pertenece esta línea
                    grupo = GrupoArticulo.objects.get(grupo_id=row['grupo_id'])
                    
                    LineaArticulo.objects.get_or_create(
                        linea_id=row['linea_id'],
                        defaults={
                            'grupo': grupo,
                            'nombre_linea': row['nombre_linea'],
                            'estado': row['estado']
                        }
                    )
            self.stdout.write(self.style.SUCCESS(f"✔ Líneas importadas desde {ruta_lineas}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importando líneas: {e}"))
            return

        # --- 3. IMPORTAR ARTÍCULOS Y CREAR LISTAS DE PRECIO ---
        self.stdout.write('Importando Artículos y creando Listas de Precios...')
        ruta_articulos = os.path.join(base_dir, 'template_articulos_clases_sipan.csv')

        try:
            with open(ruta_articulos, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Buscamos el grupo y la línea
                    grupo = GrupoArticulo.objects.get(grupo_id=row['grupo_id'])
                    linea = LineaArticulo.objects.get(linea_id=row['linea_id'])

                    # Creamos el artículo
                    articulo, created = Articulo.objects.get_or_create(
                        articulo_id=row['articulo_id'],
                        defaults={
                            'codigo_articulo': row['codigo_articulo'],
                            'codigo_barras': row['codigo_barras'] or None,
                            'descripcion': row['descripcion'],
                            'stock': row['stock'],
                            'grupo': grupo,
                            'linea': linea,
                            'estado': 1 # Asumimos estado Activo
                        }
                    )
                    
                    # Importante: Creamos su ListaPrecio asociada (vacía)
                    if created:
                        ListaPrecio.objects.create(articulo=articulo)

            self.stdout.write(self.style.SUCCESS(f"✔ Artículos importados desde {ruta_articulos}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importando artículos: {e}"))
            return

        self.stdout.write(self.style.SUCCESS('--- ¡Importación completada! ---'))