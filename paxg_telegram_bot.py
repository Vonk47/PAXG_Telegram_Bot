import requests
import time
import os
from datetime import datetime

# Configuration - Read from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
INTERVAL = 300  # 5 minutes in seconds

# Validate that required environment variables are set
if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("BOT_TOKEN and CHANNEL_ID environment variables must be set!")

def get_paxg_price():
    """Fetch PAXG price from CoinGecko API"""
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': 'pax-gold',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        price = data['pax-gold']['usd']
        change_24h = data['pax-gold'].get('usd_24h_change', 0)
        market_cap = data['pax-gold'].get('usd_market_cap', 0)
        
        return {
            'price': price,
            'change_24h': change_24h,
            'market_cap': market_cap
        }
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def format_message(price_data):
    """Format the price message"""
    if not price_data:
        return "❌ Unable to fetch PAXG price"
    
    price = price_data['price']
    change = price_data['change_24h']
    market_cap = price_data['market_cap']
    
    # Determine emoji based on price change
    trend = "📈" if change >= 0 else "📉"
    change_sign = "+" if change >= 0 else ""
    
    message = f"""
🪙 *PAXG Price Update*

💰 Price: ${price:,.2f}
{trend} 24h Change: {change_sign}{change:.2f}%
📊 Market Cap: ${market_cap:,.0f}

🕐 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
    return message

def send_telegram_message(message):
    """Send message to Telegram channel"""
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        data = {
            'chat_id': CHANNEL_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        print(f"✅ Message sent successfully at {datetime.now()}")
        return True
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def main():
    """Main loop"""
    print("🤖 PAXG Price Bot Started")
    print(f"📢 Posting to channel every {INTERVAL//60} minutes")
    
    while True:
        try:
            # Fetch price
            price_data = get_paxg_price()
            
            # Format message
            message = format_message(price_data)
            
            # Send to channel
            send_telegram_message(message)
            
            # Wait for next interval
            print(f"⏳ Waiting {INTERVAL//60} minutes until next update...")
            time.sleep(INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main()
