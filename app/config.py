import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///iis_data.db'
    SQLALCHEMY_DATABASE_URI = "postgresql://iis_db_tjj3_user:VfJaoEv80IyqQ0mpxonXxMk0iK7Cgbvp@dpg-clh4rvmg1b2c73acl9f0-a.frankfurt-postgres.render.com/iis_db_tjj3"


class TestConfig:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'