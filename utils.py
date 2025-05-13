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

# Yardımcı fonksiyonlar - Kod tekrarını azaltmak için
def clean_ticker(ticker_str):
    """Hisse kodundan '.IS' uzantısını temizler"""
    return ticker_str.replace('.IS', '')

def clean_ticker_series(series):
    """Pandas serisi içindeki hisse kodlarından '.IS' uzantısını temizler"""
    return series.str.replace('.IS', '', regex=False)

def calculate_percent_change(data, periods=1, sort=False, ascending=False, multiply_by_100=True):
    """
    Veri çerçevesindeki yüzde değişimi hesaplar
    
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

# theme_constants'dan taşınan yardımcı fonksiyonlar
def format_date(date):
    """Tarihi 'gün/ay/yıl' formatına dönüştürür"""
    return date.strftime('%d/%m/%Y')

def set_figure_template(fig):
    """Grafiklere tutarlı tema uygular"""
    # Doğrudan theme_constants'dan import etmek yerine, değerleri fonksiyon çağrıldığında alıyoruz
    # Bu sayede circular import sorununu önlüyoruz
    import theme_constants
    
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=12, color="#333333"),
        plot_bgcolor=theme_constants.PLOT_BGCOLOR,
        paper_bgcolor=theme_constants.PAPER_BGCOLOR,
        margin=dict(t=50, l=40, r=30, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='#E5E5E5',
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=11,
            font_family="Arial, sans-serif"
        ),
        xaxis=dict(
            gridcolor=theme_constants.GRID_COLOR,
            zeroline=False,
            tickfont=dict(size=10),
            title_font=dict(size=11)
        ),
        yaxis=dict(
            gridcolor=theme_constants.GRID_COLOR,
            zeroline=False,
            tickfont=dict(size=10),
            title_font=dict(size=11)
        )
    )
    return fig

def apply_figure_template(func):
    """
    Grafik fonksiyonları için dekoratör.
    Fonksiyonun döndürdüğü grafiğe otomatik olarak tema ayarlarını uygular.
    
    Kullanım:
    @apply_figure_template
    def herhangi_bir_grafik_fonksiyonu(parametreler):
        # Grafik çizimi
        fig = ...
        info_text = ...
        return fig, info_text
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, tuple) and len(result) >= 1:
            fig = result[0]
            # Tema ayarlarını uygula
            fig = set_figure_template(fig)
            # Aynı tuple'ı döndür ama fig güncellenmiş olsun
            return (fig,) + result[1:]
        return result
    return wrapper

# BIST30 hisseleri
DEFAULT_TICKERS = [
    "AEFES.IS", "AKBNK.IS", "ASELS.IS", "ASTOR.IS", "BIMAS.IS", "CIMSA.IS", "EKGYO.IS", "ENKAI.IS",
    "EREGL.IS", "FROTO.IS", "GARAN.IS", "HEKTS.IS", "ISCTR.IS", "KCHOL.IS", "KOZAL.IS", "KRDMD.IS",
    "MGROS.IS", "PETKM.IS", "PGSUS.IS", "SAHOL.IS", "SASA.IS", "SISE.IS", "TAVHL.IS", "TCELL.IS",
    "THYAO.IS", "TOASO.IS", "TTKOM.IS", "TUPRS.IS", "ULKER.IS", "YKBNK.IS"
] 

# Yardımcı formatlama fonksiyonları
def format_gains(val):
    """Kazanç değerlerini formatlayan yardımcı fonksiyon"""
    return f'<span class="dataframe-value-positive">+{val:.2f}</span>'

def format_losses(val):
    """Kayıp değerlerini formatlayan yardımcı fonksiyon"""
    return f'<span class="dataframe-value-negative">{val:.2f}</span>'

def extract_page_title(page_name):
    """Sayfa adından emoji'yi kaldırarak başlığı çıkarır"""
    return page_name.split(" ", 1)[1] if " " in page_name else page_name

def generate_market_progress_bar(positive_count, negative_count, unchanged_count, total_stocks):
    """Piyasa durumunu gösteren HTML ilerleme çubuğu oluşturur"""
    pos_percent = positive_count / total_stocks * 100
    neg_percent = negative_count / total_stocks * 100
    unc_percent = unchanged_count / total_stocks * 100
    
    segments_html = ""
    legend_html = ""
    
    # Koşullara göre HTML parçalarını oluştur
    if positive_count > 0:
        segments_html += f'<div class="progress-segment progress-segment-positive" style="width:{pos_percent}%;">{positive_count}</div>'
        legend_html += f'<div class="legend-item"><span class="legend-color-positive">■</span> Yükselen (%{pos_percent:.1f})</div>'
    
    if unchanged_count > 0:
        segments_html += f'<div class="progress-segment progress-segment-neutral" style="width:{unc_percent}%;">{unchanged_count}</div>'
        legend_html += f'<div class="legend-item"><span class="legend-color-neutral">■</span> Değişmeyen (%{unc_percent:.1f})</div>'
    
    if negative_count > 0:
        segments_html += f'<div class="progress-segment progress-segment-negative" style="width:{neg_percent}%;">{negative_count}</div>'
        legend_html += f'<div class="legend-item"><span class="legend-color-negative">■</span> Düşen (%{neg_percent:.1f})</div>'
    
    # Yatay stack bar için HTML döndür
    return f"""
    <div class="progress-container">
        <div class="progress-bar-wrapper">
            <div class="progress-bar">
                {segments_html}
            </div>
        </div>
        <div class="progress-legend">
            {legend_html}
        </div>
    </div>
    """

def generate_metric_card(label, value, subtitle, is_percentage=False, value_class=None):
    """Metrik kartı HTML'i oluşturur
    
    Args:
        label: Kart başlığı
        value: Gösterilecek değer
        subtitle: Alt başlık
        is_percentage: Değer yüzde olarak gösterilecekse True
        value_class: Değer için CSS sınıfı (positive, negative veya None)
    
    Returns:
        Metrik kartı HTML'i
    """
    # Değere yüzdelik işareti ekle
    formatted_value = f"%{value:.2f}" if is_percentage else value
    
    # CSS sınıfı ekle
    value_class_str = f" {value_class}" if value_class else ""
    
    # HTML döndür
    return f"""
    <div class="stCard metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value{value_class_str}">{formatted_value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """

def create_styled_dataframe(data, title, title_class, formatter_func=None):
    """Başlık ve biçimlendirilmiş içeriğe sahip bir veri çerçevesi oluşturur
    
    Args:
        data: Pandas DataFrame
        title: Gösterilecek başlık
        title_class: Başlık için CSS sınıfı (positive, negative)
        formatter_func: Özel biçimlendirme fonksiyonu (format_gains, format_losses gibi)
    
    Returns:
        HTML markdown için başlık ve biçimlendirilmiş DataFrame HTML'i
    """
    # Başlık HTML'i
    title_html = f'<p class="list-title list-title-{title_class}">{title}</p>'
    
    # DataFrame stil
    styled_df = data.style
    
    # Biçimlendirici fonksiyon varsa uygula
    if formatter_func and 'Getiri (%)' in data.columns:
        styled_df = styled_df.format({'Getiri (%)': formatter_func})
    
    # Stil ayarlarını uygula ve indeksi gizle
    styled_df = styled_df.hide(axis="index")
    
    # HTML olarak döndür
    df_html = styled_df.to_html()
    
    return title_html, df_html

def format_last_update(last_date, current_time=None):
    """Son güncelleme bilgisini formatlayan fonksiyon
    
    Args:
        last_date: Son veri tarihi
        current_time: Geçerli saat bilgisi (None ise şu anki zaman kullanılır)
    
    Returns:
        Son güncelleme bilgisi HTML
    """
    if current_time is None:
        import datetime
        current_time = datetime.datetime.now()
        
    update_time = f"{last_date.strftime('%d.%m.%Y')} {current_time.strftime('%H:%M')}"
    return f'<div class="last-update">Son güncelleme: {update_time}</div>' 