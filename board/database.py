import psycopg2
import psycopg2.extras
import click
import os
from flask import current_app, g

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

@click.command("init-db")
def init_db_command():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.cursor().execute(f.read().decode("utf8"))
    db.commit()
    click.echo("You successfully initialized the database!")

def get_db():
    if "db" not in g:
        db_url = os.getenv("DATABASE_URL")
        g.db = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.DictCursor)

    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
