import psycopg2
import psycopg2.extras
import click
import os
import urllib.parse
from flask import current_app, g

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

@click.command("init-db")
def init_db_command():
    db = get_db()
    with db.cursor() as cursor:
        with current_app.open_resource("schema.sql") as f:
            cursor.execute(f.read().decode("utf8"))
    db.commit()
    click.echo("You successfully initialized the database!")

def get_db():
    if "db" not in g:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL is not set in environment variables.")

        db_url = db_url.replace("postgres://", "postgresql://", 1)  # Fix Heroku-style URLs
        parsed_url = urllib.parse.urlparse(db_url)

        g.db = psycopg2.connect(
            dbname=parsed_url.path[1:],  # Remove leading '/'
            user=parsed_url.username,
            password=parsed_url.password,
            host=parsed_url.hostname,
            port=parsed_url.port,
            cursor_factory=psycopg2.extras.DictCursor,
            sslmode="require"
        )

    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
