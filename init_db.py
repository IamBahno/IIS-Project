from app import db, create_app
from app.initial_data import initial_data

app = create_app()

with app.app_context():
    # Create the tables
    db.create_all()
    initial_data(db)