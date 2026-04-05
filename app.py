from flask import Flask
from src.database.models import db

def create_app():
    app = Flask(__name__)
    # ... inside create_app() function ...
    
    from src.backend.routes import voting_api
    app.register_blueprint(voting_api)

    # Configure the database (using SQLite for local development)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///evoting.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Secure key for session management (used later for login cookies)
    app.config['SECRET_KEY'] = 'replace-this-with-a-very-long-random-string'

    # Initialize the database with the app
    db.init_app(app)

    with app.app_context():
        # This automatically creates the database tables if they don't exist
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    # Run on port 5000 with debug mode enabled for development
    app.run(debug=True, port=5000)
