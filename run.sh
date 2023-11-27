# Check if the virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found"
    exit 1
fi



venv/bin/python run.py

# Deactivate the virtual environment when you're done
deactivate