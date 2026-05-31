class NoCacheAuthMiddleware:
    """
    Middleware que agrega cabeceras HTTP anti-caché a todas las respuestas
    cuando el usuario está autenticado.

    Esto evita que el navegador muestre páginas privadas al presionar el
    botón "atrás" después de cerrar sesión.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response
