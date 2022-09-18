from flask import Flask

app = Flask(__name__, instance_relative_config=True)

# Load views
from app import views

# Setting up configuration
app.config.from_object('config')
