from decimal import Decimal
import aiohttp

class PriceProvider:
    @staticmethod
    async def get_crypto_rate(from_currency: str, to_currency: str) -> Decimal:
        FROM_COINGECKO_IDS = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "USD": "usd"
        }
        
        TO_COINGECKO_IDS = {
            "BTC": "btc",
            "ETH": "eth",
            "USD": "usd"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                from_id = FROM_COINGECKO_IDS[from_currency]
                to_id = TO_COINGECKO_IDS[to_currency]
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={from_id}&vs_currencies={to_id}"
                
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError("Failed to fetch exchange rate from CoinGecko")
                    
                    data = await response.json()
                    
                    return Decimal(str(data[from_id][to_id]))
        
        except Exception as e:
            raise ValueError(f"Error fetching crypto exchange rate: {str(e)}")
    
    @staticmethod
    async def get_fiat_rate(from_currency: str, to_currency: str) -> Decimal:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://dolarapi.com/v1/dolares/blue") as response:
                    if response.status != 200:
                        raise ValueError("Failed to fetch exchange rate from DolarAPI")
                    
                    data = await response.json()
                    venta_rate = Decimal(str(data["venta"]))
                    
                    if from_currency == "ARS" and to_currency == "USD":
                        return Decimal("1") / venta_rate
                    elif from_currency == "USD" and to_currency == "ARS":
                        return venta_rate
                    else:
                        raise ValueError(f"Unsupported currency pair: {from_currency} -> {to_currency}")
        
        except Exception as e:
            raise ValueError(f"Error fetching exchange rate: {str(e)}")