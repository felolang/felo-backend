from felo.endpoints.auth.google import api_router as google_auth_router
from felo.endpoints.translator.translator import api_router as translator_router

# from felo.endpoints.auth.google import api_router as google_auth_router

list_of_routes = [translator_router, google_auth_router]
