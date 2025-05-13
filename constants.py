# Proje genelinde kullanılan sabitler

# BIST30 hisseleri
DEFAULT_TICKERS = [
    "AEFES.IS", "AKBNK.IS", "ASELS.IS", "ASTOR.IS", "BIMAS.IS", "CIMSA.IS", "EKGYO.IS", "ENKAI.IS",
    "EREGL.IS", "FROTO.IS", "GARAN.IS", "HEKTS.IS", "ISCTR.IS", "KCHOL.IS", "KOZAL.IS", "KRDMD.IS",
    "MGROS.IS", "PETKM.IS", "PGSUS.IS", "SAHOL.IS", "SASA.IS", "SISE.IS", "TAVHL.IS", "TCELL.IS",
    "THYAO.IS", "TOASO.IS", "TTKOM.IS", "TUPRS.IS", "ULKER.IS", "YKBNK.IS"
]

# Uygulama sabitleri
DEFAULT_DATA_DAYS = 40
DEFAULT_WINDOW_SIZE = 20
DEFAULT_TOP_N = 5

# Cache ayarları
DATA_CACHE_TTL = 3600  # 1 saat (saniye cinsinden) 

# GÖRSEL TEMA SABİTLERİ
# ----------------------------------------------------

# Plotly için renk tanımları - styles.css'deki değerlerle eşleştirildi
COLOR_SCALE = ['#dc3545', '#3a86ff', '#02c076', '#8338ec', '#adb5bd', '#6c757d']
UP_COLOR = '#02c076'  # styles.css'deki --positive-color
DOWN_COLOR = '#dc3545'  # styles.css'deki --negative-color
NEUTRAL_COLOR = '#3a86ff'  # styles.css'deki --main-color
GRID_COLOR = '#f8f9fa'  # styles.css'deki --neutral-bg
PLOT_BGCOLOR = 'white'  # Grafiğin arka plan rengi
PAPER_BGCOLOR = 'white'  # Kağıt arka plan rengi

# Getiri analizi için renk skalası
RETURN_COLOR_SCALE = [DOWN_COLOR, '#ff9999', '#ffffff', '#99d98c', UP_COLOR]

# Isı haritası renk skalası
HEATMAP_COLOR_SCALE = 'Viridis'

# Tarih formatı
DATE_FORMAT = '%d/%m/%Y'
TIME_FORMAT = '%H:%M'
DATETIME_FORMAT = f"%d.%m.%Y {TIME_FORMAT}"

# Grafik özellikleri
TEXT_FONT_SIZE = 9
HOVER_TEXT_COLOR = "#333"
LINE_WIDTH = 2
GRAPH_HEIGHT = 550
HEATMAP_HEIGHT = 650
BAR_TEXT_FORMAT = '{:.2f}'
PERCENTAGE_FORMAT = '{:.2f}%' 