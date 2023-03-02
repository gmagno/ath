import asyncio
from typing import Optional

import typer
from rich import print

from app.core.config import get_settings
from app.db.session import async_session_factory

from .upload import upload_aio

cli = typer.Typer(name="Secret Santa", add_completion=False)


@cli.command()
def settings():
    settings = get_settings()
    print(settings.dict())


@cli.command()
def shell():  # pragma: no cover
    """Opens an interactive shell with objects auto imported"""
    settings = get_settings()
    _vars = {
        "settings": settings,
        "async_session_factory": async_session_factory,
        # ...
    }
    print(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(argv=[], user_ns=_vars)
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


@cli.command()
def upload(
    csv_file: Optional[str] = typer.Option("./tech-assessment.csv"),
):
    asyncio.run(upload_aio(csv_file=csv_file))


cli()
