import click
from app import create_app, _seed_admin

app = create_app()

@app.cli.command("seed")
def seed_command():
    """Crée les tables SQLAlchemy et initialise l'admin par défaut."""
    _seed_admin()
    click.echo("✓ Admin initialisé : admin@lacipres.org / 1234 (à changer !)")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
