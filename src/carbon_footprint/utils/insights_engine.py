from dataclasses import dataclass
from typing import Dict
import openai
from ..config.settings import OPENAI_API_KEY

class AIInsightsEngine:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def generate_ai_insights(self, user_data: Dict) -> str:
        # Convert string values to float before formatting
        try:
            # Create a detailed prompt for the AI
            prompt = f"""
            As a sustainability expert, analyze this user's carbon footprint data and provide specific, 
            actionable insights with estimated impact. Use the following data:

            Daily Transportation:
            - Car travel: {float(user_data['car_km']):.1f} km
            - Bus travel: {float(user_data['bus_km']):.1f} km
            - Train travel: {float(user_data['train_km']):.1f} km

            Daily Energy Usage:
            - Electricity: {float(user_data['electricity']):.1f} kWh

            Daily Diet:
            - Meat-based meals: {float(user_data['meat_meals']):.1f}
            - Vegetarian meals: {float(user_data['veg_meals']):.1f}
            - Vegan meals: {float(user_data['vegan_meals']):.1f}

            Total daily emissions: {float(user_data['total_emissions']):.1f} kg CO2

            Please provide:
            1. Specific, actionable recommendations prioritized by impact
            2. Estimated CO2 reduction for each suggestion
            3. Categorize each action as 'Easy', 'Medium', or 'Challenging'
            4. Implementation timeframe (Immediate, Short-term, Long-term)
            5. Additional context and motivation
            
            Format the response with clear sections and bullet points.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable sustainability expert providing detailed, personalized carbon footprint reduction advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except (ValueError, TypeError) as e:
            print(f"Error processing data: {e}")
            return self._generate_fallback_insights(user_data)

    def _generate_fallback_insights(self, user_data: Dict) -> str:
        """Generate basic insights if AI generation fails"""
        insights = "\n=== Carbon Footprint Insights ===\n"
        insights += "\nUnable to generate AI insights. Here are some general recommendations:\n"
        
        if user_data['car_km'] > 0:
            insights += "\n🚗 Transportation:\n"
            insights += "- Consider using public transportation more frequently\n"
            insights += "- Look into carpooling options\n"
            insights += "- Try walking or cycling for short trips\n"
        
        if user_data['electricity'] > 0:
            insights += "\n⚡ Energy Usage:\n"
            insights += "- Switch to energy-efficient appliances\n"
            insights += "- Use LED lighting\n"
            insights += "- Optimize heating and cooling\n"
        
        if user_data['meat_meals'] > 0:
            insights += "\n🥗 Diet:\n"
            insights += "- Try incorporating more plant-based meals\n"
            insights += "- Start with one meatless day per week\n"
            insights += "- Choose local and seasonal products\n"
        
        return insights 