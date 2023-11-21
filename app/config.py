import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///iis_data.db'
    SQLALCHEMY_DATABASE_URI = "postgresql://iis_db_user:3BqrkMfh0NXtlLjrSHErUL6Sryv9sixC@dpg-clefvcts40us73c0v4sg-a.frankfurt-postgres.render.com/iis_db"


class TestConfig:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'