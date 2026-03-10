from fastapi import FastAPI
from routers import r_query_news


def create_app() -> FastAPI:
    app = FastAPI(
        title="Stock News AI Agent",
        version="1.0",
        debug=False,
        docs_url="/stock-news/documentation",
    )

    return app


app = create_app()

app.include_router(r_query_news)
