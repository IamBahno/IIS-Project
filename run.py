from app import create_app
from flask import session
from datetime import timedelta
app = create_app()
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=3)
if __name__ == '__main__':
    app.run(debug=True)