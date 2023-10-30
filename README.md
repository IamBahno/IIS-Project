vytvoří vývojové prostředí a nain staluje dependencies
`./setup.sh`

aktivuje prosredi (nutne pro vytvoreni db a spousteni testu)
`source venv/bin/activate`

vytvoří db
`python init_db.py`

rozjede app
`./run.sh`


testy
`pytest tests/test_database.py` 
