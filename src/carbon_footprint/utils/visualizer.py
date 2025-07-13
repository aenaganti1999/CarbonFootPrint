import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import seaborn as sns
import os

class EmissionsVisualizer:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'visualizations')
        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        # Use a default matplotlib style instead of seaborn
        plt.style.use('default')
        # Set colors for consistency
        self.colors = ['#ff9999', '#66b3ff', '#99ff99']

    def create_emissions_breakdown(self, transport, energy, diet):
        """Create pie chart showing breakdown of emissions"""
        plt.figure(figsize=(10, 8))
        labels = ['Transport', 'Energy', 'Diet']
        sizes = [transport, energy, diet]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title('Carbon Emissions Breakdown')
        
        # Save and return the file path
        file_path = os.path.join(self.output_dir, 'emissions_breakdown.png')
        plt.savefig(file_path)
        plt.close()
        return file_path

    def plot_historical_trends(self, df):
        """Plot historical emissions trends"""
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x=df.index, y='total_emissions')
        plt.title('Historical Emissions Trends')
        plt.xlabel('Entry')
        plt.ylabel('Total Emissions (kg CO2)')
        
        # Save and return the file path
        file_path = os.path.join(self.output_dir, 'historical_trends.png')
        plt.savefig(file_path)
        plt.close()
        return file_path

    def create_comparison_chart(self, total_emissions, regional_data=None):
        """
        Create bar chart comparing user's emissions to real-time averages
        """
        plt.figure(figsize=(10, 6))
        
        # Get real-time regional emissions data if available
        if regional_data:
            regional_average = regional_data.get('average_emissions', 12)  # Default fallback
            national_average = regional_data.get('national_average', 10)   # Default fallback
        else:
            regional_average = 12  # Default fallback
            national_average = 10  # Default fallback
        
        data = [total_emissions, regional_average, national_average]
        labels = ['Your Emissions', 'Regional Average', 'National Average']
        
        plt.bar(labels, data)
        plt.title('Your Emissions Compared to Real-Time Averages')
        plt.ylabel('Daily Emissions (kg CO2)')
        
        file_path = os.path.join(self.output_dir, 'comparison_chart.png')
        plt.savefig(file_path)
        plt.close()
        return file_path 