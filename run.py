from app import create_app
from flask import session,request
from datetime import timedelta
app = create_app()
@app.before_request
def my_before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
if __name__ == '__main__':
    app.run(debug=True)