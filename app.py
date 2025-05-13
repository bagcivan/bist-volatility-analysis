import streamlit as st
from constants import DEFAULT_TICKERS, DATA_CACHE_TTL
from data_services import get_stock_data, calculate_volatility
from ui_components import (
    load_css,
    create_sidebar
)
from page_contents import render_page

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Borsa Analizi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS stillerini yükle
load_css()

# Session state ile değerleri takip et
if 'prev_data_days' not in st.session_state:
    st.session_state.prev_data_days = 40

if 'prev_window_size' not in st.session_state:
    st.session_state.prev_window_size = 20

# Sidebar arayüzünü oluştur
data_days, window_size, top_n, selected_tickers, refresh_btn, page = create_sidebar(DEFAULT_TICKERS)

# Slider değerleri değiştiğinde veriyi yenileme
if st.session_state.prev_data_days != data_days:
    st.session_state.refresh_data = True
    st.session_state.prev_data_days = data_days

if st.session_state.prev_window_size != window_size:
    st.session_state.refresh_data = True
    st.session_state.prev_window_size = window_size

# Veri yenileme butonu
if refresh_btn:
    st.session_state.refresh_data = True

# Veri yükleme fonksiyonları
@st.cache_data(ttl=DATA_CACHE_TTL)  # 1 saat cache
def fetch_stock_data(tickers, days):
    """Hisse senedi verilerini yükle"""
    with st.spinner('Hisse senedi fiyat verileri yükleniyor... Lütfen bekleyin'):
        return get_stock_data(tickers, days)

@st.cache_data(ttl=DATA_CACHE_TTL)  # 1 saat cache
def compute_volatility(data, window):
    """Varyasyon katsayısını hesapla"""
    with st.spinner('Oynaklık hesaplanıyor... Lütfen bekleyin'):
        return calculate_volatility(data, window=window)

# Veri yükleme işlemi
if 'data' not in st.session_state or 'refresh_data' in st.session_state:
    # Veri yüklemesini iki aşamaya bölerek önbellekleme etkinliğini artır
    st.session_state.data = fetch_stock_data(selected_tickers, data_days)
    st.session_state.vol_data = compute_volatility(st.session_state.data, window_size)
    
    if 'refresh_data' in st.session_state:
        del st.session_state.refresh_data
        st.success("✅ Veriler başarıyla güncellendi!")

# Ana uygulama içeriğini görüntüle
render_page(page, st.session_state.data, st.session_state.vol_data, window_size, top_n) 