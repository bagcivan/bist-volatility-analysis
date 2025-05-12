from curl_cffi import requests
import pandas as pd
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Tarayıcı gibi davranan session oluştur
session = requests.Session(impersonate="chrome")

# Veri çekme fonksiyonu
def fetch_data(ticker, period1, period2):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={period1}&period2={period2}&interval=1d"
    try:
        resp = session.get(url)
        resp.raise_for_status()
        json_data = resp.json()
        timestamps = json_data['chart']['result'][0]['timestamp']
        closes = json_data['chart']['result'][0]['indicators']['quote'][0]['close']
        dates = [datetime.datetime.fromtimestamp(ts).date() for ts in timestamps]
        return pd.Series(closes, index=pd.to_datetime(dates), name=ticker)
    except Exception as e:
        print(f"{ticker} verisi alınamadı: {e}")
        return None

def get_stock_data(tickers, days=40):
    # Tarih aralığı
    today = pd.Timestamp.today().normalize()
    now = pd.Timestamp.now()
    start_date = today - pd.Timedelta(days=days)
    period1 = int(start_date.timestamp())
    period2 = int(now.timestamp())
    
    # Paralel Veri İndirme
    all_data = pd.DataFrame()
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(fetch_data, ticker, period1, period2): ticker for ticker in tickers}
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            result = future.result()
            if result is not None:
                all_data = pd.concat([all_data, result], axis=1)
                
    return all_data

# Varyasyon katsayısı hesaplama
def calculate_volatility(data, window=20):
    cv_data = data.rolling(window=window).std() / data.rolling(window=window).mean()
    return cv_data.dropna(how="all")

# BIST30 hisseleri
DEFAULT_TICKERS = [
    "AEFES.IS", "AKBNK.IS", "ASELS.IS", "ASTOR.IS", "BIMAS.IS", "CIMSA.IS", "EKGYO.IS", "ENKAI.IS",
    "EREGL.IS", "FROTO.IS", "GARAN.IS", "HEKTS.IS", "ISCTR.IS", "KCHOL.IS", "KOZAL.IS", "KRDMD.IS",
    "MGROS.IS", "PETKM.IS", "PGSUS.IS", "SAHOL.IS", "SASA.IS", "SISE.IS", "TAVHL.IS", "TCELL.IS",
    "THYAO.IS", "TOASO.IS", "TTKOM.IS", "TUPRS.IS", "ULKER.IS", "YKBNK.IS"
] 