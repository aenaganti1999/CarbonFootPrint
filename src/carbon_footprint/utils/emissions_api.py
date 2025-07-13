import requests
from datetime import datetime
import pandas as pd
from typing import Dict, Any, Optional

class EmissionsDataAPI:
    def __init__(self):
        # EPA API endpoints and key
        self.epa_api_key = "YOUR_EPA_API_KEY"
        self.epa_base_url = "https://api.epa.gov/emissions/v1"
        
        # UNFCCC (IPCC data) API endpoint
        self.unfccc_base_url = "https://unfccc.int/news"
        
        # Carbon Interface API (provides real-time carbon intensity data)
        self.carbon_interface_key = "YOUR_CARBON_INTERFACE_KEY"
        self.carbon_interface_url = "https://www.carboninterface.com/api/v1"

    def get_regional_emissions_data(self, location: str) -> Dict[str, Any]:
        """
        Get real-time regional emissions data from EPA
        """
        try:
            endpoint = f"{self.epa_base_url}/facilities"
            params = {
                "state": location,
                "year": datetime.now().year,
                "api_key": self.epa_api_key
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching EPA data: {e}")
            return {}

    def get_grid_carbon_intensity(self, country_code: str, region: str) -> float:
        """
        Get real-time electricity grid carbon intensity from Carbon Interface API
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.carbon_interface_key}",
                "Content-Type": "application/json"
            }
            endpoint = f"{self.carbon_interface_url}/grid_intensity"
            params = {
                "country": country_code,
                "region": region
            }
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('carbon_intensity', 0.0)  # gCO2/kWh
        except requests.RequestException as e:
            print(f"Error fetching grid intensity data: {e}")
            return 0.0

    def get_ipcc_emissions_factors(self) -> Dict[str, float]:
        """
        Get hardcoded emissions factors
        """
        return {
            'car': 0.12,        # kg CO2 per km
            'bus': 0.089,       # kg CO2 per km
            'train': 0.041,     # kg CO2 per km
            'electricity': 0.233,  # kg CO2 per kWh
            'meat': 2.5,        # kg CO2 per meal
            'vegetarian': 1.0,  # kg CO2 per meal
            'vegan': 0.5        # kg CO2 per meal
        }

    def get_local_air_quality(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get real-time air quality data from EPA's AirNow API
        """
        try:
            endpoint = f"{self.epa_base_url}/airnow"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "api_key": self.epa_api_key
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching air quality data: {e}")
            return {} 