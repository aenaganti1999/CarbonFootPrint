import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from ..data.database import DataValidator

class EmissionsAnalyzer:
    def __init__(self):
        self.cluster_model = KMeans(n_clusters=3)
        self.prediction_model = RandomForestRegressor()
        self.validator = DataValidator()

    def analyze_trends(self, df):
        if len(df) < 2:
            return None

        # Clean the data
        cleaned_df = self.validator.clean_data(df)

        analysis_results = {
            'recent_emissions': cleaned_df['total_emissions'].iloc[-1],
            'avg_emissions': cleaned_df['total_emissions'].mean(),
            'trend': cleaned_df['total_emissions'].iloc[-1] - cleaned_df['total_emissions'].mean()
        }

        if len(cleaned_df) >= 5:
            features = ['car_km', 'bus_km', 'train_km', 'electricity_kwh',
                       'meat_meals', 'veg_meals', 'vegan_meals']
            
            # Ensure all features exist
            features = [f for f in features if f in cleaned_df.columns]
            
            X = cleaned_df[features].values
            y = cleaned_df['total_emissions'].values
            
            # Train on all but the last data point
            self.prediction_model.fit(X[:-1], y[:-1])
            
            # Predict the next emission
            next_prediction = self.prediction_model.predict([X[-1]])[0]
            analysis_results['next_prediction'] = next_prediction
            
            # Get feature importance
            feature_importance = dict(zip(features, 
                                       self.prediction_model.feature_importances_))
            analysis_results['feature_importance'] = feature_importance

        return analysis_results 