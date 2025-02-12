import psycopg2
import psycopg2.extras
import click
from flask import current_app, g
from urllib.parse import urlparse

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_db():
    if "db" not in g:
        db_url = current_app.config["DATABASE"]
        g.db = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.DictCursor)
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@click.command("init-db")
def init_db_command():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        sql_code = f.read().decode("utf8")
        with db.cursor() as cur:
            cur.execute(sql_code)
        db.commit()
    click.echo("Successfully initialized the database!")