# 📊 IoT Device Management System

A web app for managing IoT devices, designed for brokers to track and monitor real-world values and KPIs. Features role-based access (admin, broker, user), device and parameter management, real-time data entry with validation, and matplotlib visualizations.


## 👥 Authors

Ondřej Bahounek – database & backend  
Libor Štěpánek – UI with bootstrap
Filip Vosáhlo – testing


## ⚙️ Installation

### Local setup (Python 3.7+)
```bash
./setup.sh                # install dependencies
source venv/bin/activate # activate virtual env
python init_db.py        # initialize database
./run.sh                 # start the app