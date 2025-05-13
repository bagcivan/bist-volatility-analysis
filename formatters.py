import datetime
from constants import DATETIME_FORMAT

# Tarih formatları
def format_date(dt):
    """Tarihi Türkçe formatına çevirir"""
    if isinstance(dt, (datetime.date, datetime.datetime)):
        return dt.strftime('%d.%m.%Y')
    return str(dt)

def format_time(dt):
    """Zamanı formatlama (Saat:Dakika)"""
    if isinstance(dt, (datetime.date, datetime.datetime)):
        return dt.strftime('%H:%M')
    return str(dt)

def format_datetime(dt):
    """Tarih ve saati standart formatta gösterir"""
    if isinstance(dt, (datetime.date, datetime.datetime)):
        return dt.strftime(DATETIME_FORMAT)
    return str(dt)

# Değer formatları
def format_gains(val, use_html=True, precision=2):
    """Pozitif değişimleri formatlayan fonksiyon"""
    if use_html:
        return f'<span class="gain">+{val:.{precision}f}%</span>'
    else:
        return f'+{val:.{precision}f}%'

def format_losses(val, use_html=True, precision=2):
    """Negatif değişimleri formatlayan fonksiyon"""
    if use_html:
        return f'<span class="loss">{val:.{precision}f}%</span>'
    else:
        return f'{val:.{precision}f}%'

def format_neutral(val, use_html=True, precision=2):
    """Nötr değişimleri formatlayan fonksiyon"""
    if use_html:
        return f'<span class="neutral">{val:.{precision}f}%</span>'
    else:
        return f'{val:.{precision}f}%'

def format_percent_change(val, use_html=True, precision=2):
    """Değişimleri durumuna göre farklı formatlayan fonksiyon"""
    if val > 0:
        return format_gains(val, use_html, precision)
    elif val < 0:
        return format_losses(val, use_html, precision)
    else:
        return format_neutral(val, use_html, precision)

def format_currency(val, currency='₺', precision=2):
    """Para birimini formatlayan fonksiyon"""
    return f'{val:.{precision}f} {currency}'

def format_duration(seconds):
    """Süreyi formatlayan fonksiyon"""
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    
    if hours > 0:
        return f"{int(hours)}s {int(mins)}dk"
    elif mins > 0:
        return f"{int(mins)}dk {int(secs)}sn"
    else:
        return f"{int(secs)}sn"

# Hisse kodu temizleme fonksiyonları
def clean_ticker(ticker_str):
    """Hisse kodundan '.IS' uzantısını temizler"""
    return ticker_str.replace('.IS', '')

def clean_ticker_series(series):
    """Pandas serisi içindeki hisse kodlarından '.IS' uzantısını temizler"""
    return series.str.replace('.IS', '', regex=False) 