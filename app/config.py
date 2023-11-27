import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'

    #connect link to db on server
    SQLALCHEMY_DATABASE_URI = "postgresql://iis_db_tjj3_user:VfJaoEv80IyqQ0mpxonXxMk0iK7Cgbvp@dpg-clh4rvmg1b2c73acl9f0-a.frankfurt-postgres.render.com/iis_db_tjj3"

    #if you want create db locally, comment the link above and use this instead 
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///iis_data.db'
    


class TestConfig:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    #for testing only, create db in-memory 
    SQLALCHEMY_DATABASE_URI = 'sqlite://'