import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Emission factors (kg CO2 per unit)
EMISSION_FACTORS = {
    'car': 0.12,        # kg CO2 per km
    'bus': 0.089,       # kg CO2 per km
    'train': 0.041,     # kg CO2 per km
    'electricity': 0.233,  # kg CO2 per kWh
    'meat': 2.5,        # kg CO2 per meal
    'vegetarian': 1.0,  # kg CO2 per meal
    'vegan': 0.5        # kg CO2 per meal
}

# API keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EPA_API_KEY = os.getenv('EPA_API_KEY')
CARBON_INTERFACE_KEY = os.getenv('CARBON_INTERFACE_KEY')

# Database Configuration
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                            'data', 'carbon_footprint.db')