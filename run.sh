# Check if the virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found"
    exit 1
fi

# # Run your Flask application
# export FLASK_APP=app.py  # Replace with your Flask app entry point
# export FLASK_ENV=development  # Set to 'production' for production

venv/bin/python run.py

# Deactivate the virtual environment when you're done
deactivate