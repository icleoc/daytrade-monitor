import os
import logging
from twelvedata import TDClient

logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv("TWELVE_API_KEY")

td = TDClient(apikey=API_KEY)


def fetch_symbol_data(symbol: str, interval: str = "15min"):
    """
    Busca OHLCV do símbolo no intervalo desejado.
    """
    try:
        logging.info(f"Buscando dados para {symbol} ({interval})...")

        ts = td.time_series(
            symbol=symbol,
            interval=interval,
            outputsize=1
        )

        data = ts.as_json()

        if not data or "values" not in data or len(data["values"]) == 0:
            raise ValueError(f"Nenhum dado retornado para {symbol}")

        latest = data["values"][0]

        return {
            "symbol": symbol,
            "open": float(latest["open"]),
            "high": float(latest["high"]),
            "low": float(latest["low"]),
            "close": float(latest["close"]),
            "volume": float(latest.get("volume", 0))
        }

    except Exception as e:
        logging.error(f"Erro ao buscar {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}


def get_all_symbols_data(symbols):
    """
    Retorna dados atualizados de múltiplos símbolos.
    """
    results = []

    for s in symbols:
        results.append(fetch_symbol_data(s))

    return results


# Conversão opcional caso queira exibir nomes amigáveis no dashboard
def normalize_symbol(symbol: str):
    mapping = {
        "BTC/USDT": "Bitcoin",
        "ETH/USDT": "Ethereum",
        "EUR/USD": "Euro x Dólar",
        "XAU/USD": "Ouro"
    }
    return mapping.get(symbol, symbol)
