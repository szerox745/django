from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para DRF.
    Devuelve errores en un formato JSON estandarizado.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'status_code': response.status_code,
            'error': True,
            'message': response.data.get('detail', 'Ocurrió un error')
        }

        if 'detail' not in response.data:
             custom_data['details'] = response.data

        response.data = custom_data

    else:
        response_data = {
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'error': True,
            'message': 'Error interno del servidor.'
        }

        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response