import streamlit as st
from src.carbon_footprint.bot.carbon_bot import CarbonFootprintBot
from src.carbon_footprint.utils.news_fetcher import NewsFetcher

# Initialize the bot
bot = CarbonFootprintBot()

# App title
st.title("🌍 Carbon Footprint Calculator & Chat")

# Sidebar for carbon footprint calculation
st.sidebar.header("Carbon Footprint Calculator")
car_km = st.sidebar.number_input("Car Kilometers per Day", min_value=0.0, value=10.0)
bus_km = st.sidebar.number_input("Bus Kilometers per Day", min_value=0.0, value=5.0)
train_km = st.sidebar.number_input("Train Kilometers per Day", min_value=0.0, value=0.0)
electricity = st.sidebar.number_input("Electricity Usage (kWh per Day)", min_value=0.0, value=10.0)
meat_meals = st.sidebar.number_input("Meat-Based Meals per Day", min_value=0, value=2)
veg_meals = st.sidebar.number_input("Vegetarian Meals per Day", min_value=0, value=1)
vegan_meals = st.sidebar.number_input("Vegan Meals per Day", min_value=0, value=0)

# Collect user data
user_data = {
    'car_km': car_km,
    'bus_km': bus_km,
    'train_km': train_km,
    'electricity': electricity,
    'meat_meals': meat_meals,
    'veg_meals': veg_meals,
    'vegan_meals': vegan_meals
}

# Calculate emissions
if st.sidebar.button("Calculate Carbon Footprint"):
    with st.spinner("Calculating your carbon footprint..."):
        emissions_data = bot.process_user_data(user_data)
        
        # Show results
        st.header("📊 Your Carbon Footprint Results")
        st.metric("Daily Emissions", f"{emissions_data['total']:.2f} kg CO2")
        st.metric("Yearly Emissions", f"{emissions_data['yearly_total']:.2f} kg CO2")
        
        # Show emissions breakdown
        st.subheader("Emissions Breakdown")
        col1, col2, col3 = st.columns(3)
        col1.metric("Transport", f"{emissions_data['transport']:.2f} kg CO2")
        col2.metric("Energy", f"{emissions_data['energy']:.2f} kg CO2")
        col3.metric("Diet", f"{emissions_data['diet']:.2f} kg CO2")
        
        # Show visualizations
        st.subheader("Visualizations")
        visualization_paths = bot.get_visualizations(emissions_data)
        for viz_type, path in visualization_paths.items():
            st.image(path, caption=viz_type.replace("_", " ").title())
        
        # Show recommendations
        st.subheader("🌱 Recommendations")
        recommendations = bot.get_recommendations(emissions_data)
        st.write(recommendations)

# Chat interface
st.header("💬 Chat with the Carbon Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about carbon footprint"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response
    with st.spinner("Thinking..."):
        response = bot.generate_chat_response(prompt)
    
    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Example chat
st.subheader("Example Chat")
st.write("User: How can I reduce my carbon footprint?")
st.write("Assistant: Here are some suggestions:")
st.write("1. Switch to an electric vehicle → Save up to 3.0 kg CO2 daily.")
st.write("2. Use public transport → Save up to 2.0 kg CO2 daily.")
st.write("3. Reduce meat consumption → Save up to 1.5 kg CO2 daily.")

st.write("User: What's the carbon impact of flying?")
st.write("Assistant: Flying has a significant carbon impact. For example:")
st.write("- A short-haul flight (500 km) emits about 150 kg CO2 per passenger.")
st.write("- A long-haul flight (10,000 km) emits about 1,500 kg CO2 per passenger.")
st.write("Consider alternatives like trains or video conferencing when possible.")

# Add News Section
st.header("📰 Daily Sustainability News")

# Initialize news fetcher
news_fetcher = NewsFetcher()

# Add refresh button
if st.button("🔄 Refresh News"):
    with st.spinner("Fetching latest sustainability news..."):
        news_articles = news_fetcher.fetch_sustainability_news(days=1)
        
        if news_articles:
            for article in news_articles:
                with st.expander(f"📌 {article['title']}"):
                    st.write(f"**Summary**: {article['summary']}")
                    st.write(f"**Source**: {article['source']}")
                    st.write(f"**Published**: {article['published_at']}")
                    st.markdown(f"[Read more]({article['url']})")
        else:
            st.warning("No news articles found. Please try again later.") 