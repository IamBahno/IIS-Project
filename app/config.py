import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///iis_data.db'
    SQLALCHEMY_DATABASE_URI = "postgresql://database_iis_user:oXw4NYeGCGsLijU0AfRSOi2sWydCGibP@dpg-cled936f27hc738sh7rg-a.frankfurt-postgres.render.com/database_iis"


class TestConfig:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'