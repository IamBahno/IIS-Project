from app import db, create_app

app = create_app()

with app.app_context():
    # Create the tables
    db.create_all()