import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///iis_data.db'
    SQLALCHEMY_DATABASE_URI = "postgresql://iis_db_9hn8_user:gP6anVVqmvsth6ulLcGkiNWlzBhXp4zH@dpg-clf40gmf27hc73bifplg-a.frankfurt-postgres.render.com/iis_db_9hn8"


class TestConfig:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'