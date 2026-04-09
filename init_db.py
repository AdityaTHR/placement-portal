import os
from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash

def init_db():
    app = Flask(__name__)
    # Ensure current working directory is used for the database
    db_path = os.path.join(os.getcwd(), 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                email='admin@placement.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Database initialized and Admin user created.")
        else:
            print("Database already initialized.")

if __name__ == '__main__':
    init_db()
