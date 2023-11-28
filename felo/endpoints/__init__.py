from felo.endpoints.api.api import api_router as api_router
from felo.endpoints.translator.translator import api_router as translator_router

# from felo.endpoints.auth.google import api_router as google_auth_router

list_of_routes = [api_router, translator_router]
