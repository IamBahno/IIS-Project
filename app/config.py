import os


class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'

    #connect link to db on server
    SQLALCHEMY_DATABASE_URI = "postgresql://iis_db_0m35_user:Pt4pSDepOhhFMEFzieKsk4Qn4KVppxRD@dpg-clic5nsig7qc73d147jg-a.frankfurt-postgres.render.com/iis_db_0m35"

    #if you want create db locally, comment the link above and use this instead 
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///iis_data.db'
    


class TestConfig:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    #for testing only, create db in-memory 
    SQLALCHEMY_DATABASE_URI = 'sqlite://'