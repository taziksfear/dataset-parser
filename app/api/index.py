from flask import Flask
from app import create_app

app = create_app()

from app.routes import bp as routes_bp
app.register_blueprint(routes_bp)

if __name__ == "__main__":
    app.run()