from carbon_footprint.bot.carbon_bot import CarbonFootprintBot
import argparse

def main():
    parser = argparse.ArgumentParser(description='Carbon Footprint Calculator')
    parser.add_argument('--mode', choices=['terminal', 'api', 'chat'],
                       help='Run in terminal, API, or chat mode')
    parser.add_argument('--location', nargs=3, metavar=('LATITUDE', 'LONGITUDE', 'REGION'),
                       help='Your location (latitude longitude region)')
    
    args = parser.parse_args()
    
    # Initialize the bot
    bot = CarbonFootprintBot()
    
    # Set location if provided
    if args.location:
        lat, lon, region = args.location
        bot.set_user_location(float(lat), float(lon), region)
    
    if args.mode == 'chat':
        bot.chat_interface()
    elif args.mode == 'terminal':
        bot.terminal_interface()
    else:
        print("API mode - Please use the API endpoints directly")

if __name__ == "__main__":
    main()