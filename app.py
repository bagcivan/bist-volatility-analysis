import streamlit as st
from utils import get_stock_data, calculate_volatility, DEFAULT_TICKERS
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

# Veri yükleme fonksiyonu
@st.cache_data(ttl=3600)  # 1 saat cache
def load_data(tickers, days, window=20):
    with st.spinner('Veriler yükleniyor... Lütfen bekleyin'):
        data = get_stock_data(tickers, days)
        vol_data = calculate_volatility(data, window=window)
        return data, vol_data

# Veri yükleme işlemi
if 'data' not in st.session_state or 'refresh_data' in st.session_state:
    st.session_state.data, st.session_state.vol_data = load_data(selected_tickers, data_days, window=window_size)
    if 'refresh_data' in st.session_state:
        del st.session_state.refresh_data
        st.success("✅ Veriler başarıyla güncellendi!")

# Ana uygulama içeriğini görüntüle
render_page(page, st.session_state.data, st.session_state.vol_data, window_size, top_n) 