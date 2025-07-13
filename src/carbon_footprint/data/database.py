import sqlite3
import os
from datetime import datetime
from ..config.settings import DATABASE_PATH
import pandas as pd
import numpy as np
from scipy import stats

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        # Create the data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def initialize_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    car_km FLOAT,
                    bus_km FLOAT,
                    train_km FLOAT,
                    electricity_kwh FLOAT,
                    meat_meals FLOAT,
                    veg_meals FLOAT,
                    vegan_meals FLOAT,
                    total_emissions FLOAT
                )
            ''')
            conn.commit()

    def save_user_data(self, data_dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_data (
                    timestamp, car_km, bus_km, train_km, electricity_kwh,
                    meat_meals, veg_meals, vegan_meals, total_emissions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                data_dict['car_km'],
                data_dict['bus_km'],
                data_dict['train_km'],
                data_dict['electricity'],
                data_dict['meat_meals'],
                data_dict['veg_meals'],
                data_dict['vegan_meals'],
                data_dict['total_emissions']
            ))
            conn.commit()

class DataValidator:
    @staticmethod
    def clean_data(df):
        """
        Handle missing values and outliers in the dataset
        """
        # Create a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Handle missing values
        cleaned_df = DataValidator.handle_missing_values(cleaned_df)
        
        # Handle outliers
        cleaned_df = DataValidator.handle_outliers(cleaned_df)
        
        return cleaned_df

    @staticmethod
    def handle_missing_values(df):
        """
        Handle missing values in the dataset
        """
        # Fill missing values with column means
        for col in df.columns:
            if df[col].dtype in [np.float64, np.int64]:
                df[col].fillna(df[col].mean(), inplace=True)
        
        return df

    @staticmethod
    def handle_outliers(df, z_threshold=3):
        """
        Handle outliers using z-score method
        """
        # Only process numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Calculate z-scores
            z_scores = np.abs(stats.zscore(df[col]))
            
            # Replace outliers with column median
            df.loc[z_scores > z_threshold, col] = df[col].median()
        
        return df

    @staticmethod
    def validate_input(data_dict):
        """
        Validate user input values
        """
        valid_data = {}
        
        for key, value in data_dict.items():
            try:
                # Convert to float and ensure non-negative
                value = float(value)
                if value < 0:
                    raise ValueError("Negative values not allowed")
                valid_data[key] = value
            except (ValueError, TypeError):
                # If invalid, set to 0
                valid_data[key] = 0.0
        
        return valid_data 