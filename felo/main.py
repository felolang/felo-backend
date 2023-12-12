import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from openai import OpenAI
from starlette.middleware.sessions import SessionMiddleware

from felo.config.default import DefaultSettings
from felo.config.utils import CONFIG

# from
from felo.endpoints import list_of_routes


def bind_routes(application: FastAPI, config: DefaultSettings) -> None:
    """
    Bind all routes to application.
    """
    for route in list_of_routes:
        application.include_router(route, prefix=config.PATH_PREFIX)


def get_app(lifespan=None) -> FastAPI:
    description = "Backend for felo project"
    application = FastAPI(
        lifespan=lifespan,
        title="Felo",
        description=description,
        docs_url="/swagger",
        openapi_url="/openapi",
        version="0.1.0",
    )
    # application.mount("/auth", auth_app)

    bind_routes(application, CONFIG)
    application.state.settings = CONFIG
    return application


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = OpenAI()

    assistant_instruction = """ You are a translation assistant. As input you receive JSON, which contains the original language, the language into which you want to translate, and the piece of text itself (example: {"soruce_language": "ENG", "target_language": "RUS", "selected_text": "called", " context": "They've called off the meeting."}).
        Always return the result in JSON format. The result should be the following fields:
        "text_translation" - translation of the selected text itself;
        "text_in_context" - translation of text taking into account the context
        "part_of_speach" - part of speech of the selected text
    """

    # assistant = client.beta.assistants.create(
    #     name="Felo translator",
    #     instructions=assistant_instruction,
    #     model="gpt-3.5-turbo-1106",
    # )
    yield


app = get_app(lifespan=lifespan)
SECRET_KEY = os.environ.get("SECRET_KEY") or None
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


ALLOWED_HOSTS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return HTMLResponse('<body><a href="api/v1/auth/login">Log In</a></body>')


@app.get("/main")
async def token(request: Request):
    return HTMLResponse(
        f"""
                <script>
                function send(){{
                    var req = new XMLHttpRequest();
                    req.onreadystatechange = function() {{
                        if (req.readyState === 4) {{
                            console.log(req.response);
                            if (req.response["result"] === true) {{
                                window.localStorage.setItem('jwt', req.response["access_token"]);
                            }}
                        }}
                    }}
                    req.withCredentials = true;
                    req.responseType = 'json';
                    req.open("post", "api/v1/auth/token?"+window.location.search.substr(1), true);
                    req.send("");

                }}
                </script>
                <button onClick="send()">Get FastAPI JWT Token</button>

                <button onClick='fetch("{CONFIG.FRONTEND_URL}/api/v1/api/").then(
                    (r)=>r.json()).then((msg)=>{{console.log(msg)}});'>
                Call Unprotected API
                </button>
                <button onClick='fetch("{CONFIG.FRONTEND_URL}/api/v1/api/protected").then(
                    (r)=>r.json()).then((msg)=>{{console.log(msg)}});'>
                Call Protected API without JWT
                </button>
                <button onClick='fetch("{CONFIG.FRONTEND_URL}/api/v1/api/protected",{{
                    headers:{{
                        "Authorization": "Bearer " + window.localStorage.getItem("jwt")
                    }},
                }}).then((r)=>r.json()).then((msg)=>{{console.log(msg)}});'>
                Call Protected API wit JWT
                </button>
                <button onClick='fetch("{0}/api/v1/auth/logout",{{
                    headers:{{
                        "Authorization": "Bearer " + window.localStorage.getItem("jwt")
                    }},
                }}).then((r)=>r.json()).then((msg)=>{{
                    console.log(msg);
                    if (msg["result"] === true) {{
                        window.localStorage.removeItem("jwt");
                    }}
                    }});'>
                Logout
                </button>
        """
    )
