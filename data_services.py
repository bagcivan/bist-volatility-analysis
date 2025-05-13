from curl_cffi import requests
import pandas as pd
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import memoize

# Tarayıcı gibi davranan session oluştur
session = requests.Session(impersonate="chrome")

# Veri çekme fonksiyonu
def fetch_data(ticker, period1, period2):
    """Yahoo Finance'den hisse senedi verilerini çeker
    
    Args:
        ticker: Hisse kodu (örn. "THYAO.IS")
        period1: Başlangıç tarihi timestamp
        period2: Bitiş tarihi timestamp
    
    Returns:
        Fiyat serisi veya hata durumunda None
    """
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
    """Birden fazla hisse senedi için verileri paralel olarak çeker
    
    Args:
        tickers: Hisse kodları listesi
        days: Kaç günlük veri isteniyor
    
    Returns:
        Tüm hisse senetlerinin fiyat verilerini içeren DataFrame
    """
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
    """Varyasyon katsayısı (Oynaklık) hesaplar
    
    Args:
        data: Fiyat verileri DataFrame
        window: Pencere boyutu (gün)
    
    Returns:
        Varyasyon katsayısı DataFrame'i
    """
    cv_data = data.rolling(window=window).std() / data.rolling(window=window).mean()
    return cv_data.dropna(how="all")

@memoize
def calculate_percent_change(data, periods=1, sort=False, ascending=False, multiply_by_100=True):
    """Veri çerçevesindeki yüzde değişimi hesaplar
    
    Args:
        data: Veri çerçevesi
        periods: Karşılaştırma dönemi
        sort: Sonuçları sıralamak için
        ascending: Artan sıralama için True, azalan için False
        multiply_by_100: Yüzde değerleri için 100 ile çarp
        
    Returns:
        Yüzde değişim serisi
    """
    changes = data.pct_change(periods=periods).iloc[-1]
    
    if multiply_by_100:
        changes = changes * 100
        
    if sort:
        changes = changes.sort_values(ascending=ascending)
        
    return changes

def calculate_drawdown(df, price_col='Close'):
    """Zirveden uzaklık (drawdown) hesaplar
    
    Args:
        df: Fiyat serisini içeren DataFrame
        price_col: Fiyat sütununun adı
        
    Returns:
        Peak ve Drawdown sütunları eklenmiş DataFrame
    """
    # Geçici DataFrame oluştur
    temp_df = df.copy()
    
    # Zirve fiyatları hesapla (kümülatif maksimum)
    temp_df['Peak'] = temp_df[price_col].cummax()
    
    # Zirveden uzaklık (yüzde olarak)
    temp_df['Drawdown'] = (temp_df[price_col] - temp_df['Peak']) / temp_df['Peak'] * 100
    
    return temp_df 