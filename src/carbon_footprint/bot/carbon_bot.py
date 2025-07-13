import openai
from ..config.settings import EMISSION_FACTORS, OPENAI_API_KEY
from ..data.database import Database, DataValidator
from ..models.ml_models import EmissionsAnalyzer
from ..utils.visualizer import EmissionsVisualizer
from ..utils.insights_engine import AIInsightsEngine
from ..utils.emissions_api import EmissionsDataAPI
import pandas as pd
from typing import Dict, Any

class CarbonFootprintBot:
    def __init__(self):
        self.emission_factors = EMISSION_FACTORS
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.db = Database()
        self.analyzer = EmissionsAnalyzer()
        self.visualizer = EmissionsVisualizer()
        self.validator = DataValidator()
        self.last_input = {}
        self.db.initialize_database()
        self.emissions_api = EmissionsDataAPI()
        self.user_location = None
        self.user_region = None
        self.conversation_history = []
        self.user_context = {}

    def set_user_location(self, latitude: float, longitude: float, region: str):
        """
        Set user's location for more accurate emissions calculations
        """
        self.user_location = (latitude, longitude)
        self.user_region = region

    def process_user_data(self, user_data):
        """
        Process user input data regardless of source (API, terminal, frontend)
        """
        # Store the last input
        self.last_input = user_data.copy()
        
        # Validate input
        valid_data = self.validator.validate_input(user_data)
        
        # Calculate all emissions
        emissions_breakdown = self.calculate_emissions(valid_data)
        
        # Save data
        self.db.save_user_data({**valid_data, 'total_emissions': emissions_breakdown['total']})
        
        return emissions_breakdown

    def calculate_emissions(self, valid_data):
        """
        Calculate emissions using real-time data where available
        """
        # Get real-time grid carbon intensity if location is set
        if self.user_region:
            grid_intensity = self.emissions_api.get_grid_carbon_intensity(
                country_code="US",  # Update based on user's country
                region=self.user_region
            )
        else:
            grid_intensity = self.emission_factors['electricity']

        # Get latest IPCC emissions factors
        ipcc_factors = self.emissions_api.get_ipcc_emissions_factors()
        
        # Calculate transport emissions using IPCC factors if available
        transport_emissions = (
            valid_data['car_km'] * (ipcc_factors.get('car', self.emission_factors['car'])) +
            valid_data['bus_km'] * (ipcc_factors.get('bus', self.emission_factors['bus'])) +
            valid_data['train_km'] * (ipcc_factors.get('train', self.emission_factors['train']))
        )
        
        # Calculate energy emissions using real-time grid intensity
        energy_emissions = valid_data['electricity'] * grid_intensity
        
        # Calculate diet emissions
        diet_emissions = (
            valid_data['meat_meals'] * (ipcc_factors.get('meat', self.emission_factors['meat'])) +
            valid_data['veg_meals'] * (ipcc_factors.get('vegetarian', self.emission_factors['vegetarian'])) +
            valid_data['vegan_meals'] * (ipcc_factors.get('vegan', self.emission_factors['vegan']))
        )

        # Get local air quality data if location is set
        air_quality = {}
        if self.user_location:
            air_quality = self.emissions_api.get_local_air_quality(
                latitude=self.user_location[0],
                longitude=self.user_location[1]
            )

        total_emissions = transport_emissions + energy_emissions + diet_emissions
        
        return {
            'transport': transport_emissions,
            'energy': energy_emissions,
            'diet': diet_emissions,
            'total': total_emissions,
            'yearly_total': total_emissions * 365,
            'air_quality': air_quality,
            'grid_intensity': grid_intensity
        }

    def get_visualizations(self, emissions_data):
        """
        Generate all visualizations based on emissions data
        """
        df = pd.read_sql_query("SELECT * FROM user_data", self.db.get_connection())
        
        visualization_paths = {
            'breakdown': self.visualizer.create_emissions_breakdown(
                emissions_data['transport'],
                emissions_data['energy'],
                emissions_data['diet']
            ),
            'historical': self.visualizer.plot_historical_trends(df),
            'comparison': self.visualizer.create_comparison_chart(emissions_data['total'])
        }
        
        return visualization_paths

    def get_recommendations(self, emissions_data):
        """
        Generate AI-powered recommendations based on emissions data
        """
        user_data = {
            **self.last_input,
            'total_emissions': emissions_data['total']
        }
        
        insights_engine = AIInsightsEngine()
        return insights_engine.generate_ai_insights(user_data)

    def get_terminal_input(self):
        """
        Collect user input through terminal interface
        """
        return {
            'car_km': input("How many kilometers do you drive per day? "),
            'bus_km': input("How many kilometers do you travel by bus per day? "),
            'train_km': input("How many kilometers do you travel by train per day? "),
            'electricity': input("How many kWh of electricity do you use per day? "),
            'meat_meals': input("How many meat-based meals do you eat per day? "),
            'veg_meals': input("How many vegetarian meals do you eat per day? "),
            'vegan_meals': input("How many vegan meals do you eat per day? ")
        }
        
    def terminal_interface(self):
        """
        Run the bot in terminal interface mode
        """
        print("Welcome to the Carbon Footprint Calculator Bot!")
        print("I'll help you understand and reduce your carbon footprint.")
        
        # Get user input
        user_data = self.get_terminal_input()
        
        # Process data and get results
        emissions_data = self.process_user_data(user_data)
        
        # Show results
        print("\n=== Your Carbon Footprint Results ===")
        print(f"Your estimated daily carbon footprint is: {emissions_data['total']:.2f} kg CO2")
        print(f"Yearly estimate: {emissions_data['yearly_total']:.2f} kg CO2")
        
        # Generate and show visualizations
        visualization_paths = self.get_visualizations(emissions_data)
        print("\nVisualizations have been saved to:")
        print(f"- Emissions Breakdown: Shows the proportion of emissions from each source")
        print(f"- Historical Trends: Shows how your carbon footprint has changed over time")
        print(f"- Comparison Chart: Compares your carbon footprint to the average person")
        
        # Get and show recommendations
        recommendations = self.get_recommendations(emissions_data)
        print("\n=== Analyzing Your Carbon Footprint ===")
        print(recommendations)
        
        return emissions_data

    def api_interface(self, user_data):
        """
        Handle API requests
        """
        emissions_data = self.process_user_data(user_data)
        visualization_paths = self.get_visualizations(emissions_data)
        recommendations = self.get_recommendations(emissions_data)
        
        return {
            'emissions': emissions_data,
            'visualizations': visualization_paths,
            'recommendations': recommendations
        }

    def get_predictive_insights(self, emissions_data: dict) -> str:
        """
        Use AI to analyze the user's carbon footprint and provide thoughtful, context-aware insights
        """
        try:
            # Prepare a detailed prompt for AI
            prompt = f"""
            You are a sustainability expert analyzing a user's carbon footprint. Here is their data:
            - Transport Emissions: {emissions_data['transport']} kg CO2 (daily)
            - Energy Emissions: {emissions_data['energy']} kg CO2 (daily)
            - Diet Emissions: {emissions_data['diet']} kg CO2 (daily)
            - Total Emissions: {emissions_data['total']} kg CO2 (daily)

            Your task:
            1. Analyze the data and identify the user's biggest source of emissions.
            2. Provide 3 specific, actionable suggestions to reduce their footprint.
            3. For each suggestion, estimate the potential carbon savings.
            4. Write a short, encouraging message to motivate the user.

            Format your response as follows:
            **Analysis**: [Your analysis of the data]
            **Suggestions**:
            1. [Suggestion 1] → [Estimated savings]
            2. [Suggestion 2] → [Estimated savings]
            3. [Suggestion 3] → [Estimated savings]
            **Motivation**: [Encouraging message]
            """

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                    "role": "system", 
                    "content": "You are a sustainability expert. Provide thoughtful, actionable insights."
                    },
                    {
                    "role": "user",
                    "content": prompt}
                ],
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating predictive insights: {e}")
            return "Unable to generate insights at this time."

    def chat_interface(self):
        """
        Interactive chat interface for carbon footprint discussions
        """
        print("Welcome to Carbon Footprint Assistant! 👋")
        print("I can help you understand and reduce your carbon footprint.")
        print("Type 'exit' to end the conversation or 'calculate' to measure your footprint.")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                print("\nGoodbye! Keep making sustainable choices! 🌱")
                break
                
            if user_input.lower() == 'calculate':       
                emissions_data = self.terminal_interface()
                self.user_context['emissions_data'] = emissions_data
                continue
            
            response = self.generate_chat_response(user_input)
            print(f"\nAssistant: {response}")

    def generate_chat_response(self, user_input: str) -> str:
        """
        Generate contextual responses to user questions
        """
        try:
            # Build context from previous calculations
            context = ""
            if self.user_context.get('emissions_data'):
                emissions = self.user_context['emissions_data']
                context = f"""
                User's carbon footprint data:
                - Daily emissions: {emissions['total']:.2f} kg CO2
                - Transport: {emissions['transport']:.2f} kg CO2
                - Energy: {emissions['energy']:.2f} kg CO2
                - Diet: {emissions['diet']:.2f} kg CO2
                """

            # Create the conversation prompt
            messages = [
                {"role": "system", "content": """
                You are a knowledgeable and helpful sustainability expert. 
                Provide specific, actionable advice about carbon footprint reduction.
                Be conversational and encouraging, but also direct and practical.
                Use emojis occasionally to make the conversation engaging.
                If you don't know something, admit it and suggest alternatives.
                """},
                *self.conversation_history,
                {"role": "user", "content": f"""
                Context: {context}
                
                User Question: {user_input}
                
                Provide a helpful, specific response. If the user hasn't calculated their footprint yet,
                encourage them to type 'calculate' to measure their impact.
                """}
            ]

            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )

            # Store conversation history (keep last 5 exchanges)
            self.conversation_history.append({"role": "user", "content": user_input})
            assistant_response = response.choices[0].message.content.strip()
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return assistant_response

        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response. Please try again."