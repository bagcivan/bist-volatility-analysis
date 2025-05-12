import streamlit as st
import pandas as pd
import datetime
import time
from utils import get_stock_data, calculate_volatility, DEFAULT_TICKERS
from visualizations import (
    plot_top_volatile_stocks, 
    plot_volatility_heatmap, 
    plot_last_day_volatility,
    plot_momentum_analysis,
    plot_volatility_vs_return,
    plot_sharpe_ratio,
    plot_price_drawdown
)

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Borsa Oynaklık Analizi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Sidebar ayarları
st.sidebar.title("Borsa Oynaklık Analizi")

# Veri parametreleri
data_days = st.sidebar.slider("Kaç günlük veri alınsın?", 30, 180, 40)
window_size = st.sidebar.slider("Oynaklık hesaplama penceresi (gün)", 10, 30, 20)
top_n = st.sidebar.slider("Kaç hisse gösterilsin?", 3, 10, 5)

# Hisse seçimi
use_default = st.sidebar.checkbox("BIST-30 Hisseleri", value=True)

if use_default:
    selected_tickers = DEFAULT_TICKERS
else:
    custom_tickers = st.sidebar.text_area(
        "Özel hisse kodları (her satıra bir hisse kodu girin, örneğin: THYAO.IS)",
        value="\n".join(DEFAULT_TICKERS[:5]),
        height=150
    )
    selected_tickers = [t.strip() for t in custom_tickers.split("\n") if t.strip()]

# Veri yenileme butonu
if st.sidebar.button("Verileri Yenile"):
    st.session_state.refresh_data = True
    
# Sayfa seçimi
page = st.sidebar.radio(
    "Gösterge Seçimi", 
    ["Tüm Analizler", "En Oynak Hisseler", "Isı Haritası", "Son Gün Oynaklık", 
     "Momentum Analizi", "Oynaklık vs Getiri", "Risk-Getiri Analizi", "Zirveden Uzaklık"]
)

# Veri yükleme
@st.cache_data(ttl=3600)  # 1 saat cache
def load_data(tickers, days):
    with st.spinner('Veriler yükleniyor...'):
        data = get_stock_data(tickers, days)
        vol_data = calculate_volatility(data, window=window_size)
        return data, vol_data

# Ana içerik


# Veri yükleme mantığı
if 'data' not in st.session_state or 'refresh_data' in st.session_state:
    st.session_state.data, st.session_state.vol_data = load_data(selected_tickers, data_days)
    if 'refresh_data' in st.session_state:
        del st.session_state.refresh_data
        st.success("Veriler yenilendi!")

all_data = st.session_state.data
cv_data = st.session_state.vol_data

# Son veri tarihini göster
if not all_data.empty:
    st.caption(f"Son veri tarihi: {all_data.index[-1].date()}")

# Sayfaya göre içerik gösterme
if page == "Tüm Analizler" or page == "En Oynak Hisseler":
    st.header("En Oynak Hisseler")
    fig1, info_text1 = plot_top_volatile_stocks(cv_data, top_n=top_n)
    st.info(info_text1)
    st.plotly_chart(fig1, use_container_width=True)

if page == "Tüm Analizler" or page == "Isı Haritası":
    st.header("Oynaklık Isı Haritası")
    fig2, info_text2 = plot_volatility_heatmap(cv_data)
    st.info(info_text2)
    st.plotly_chart(fig2, use_container_width=True)

if page == "Tüm Analizler" or page == "Son Gün Oynaklık":
    st.header("Son Gün Oynaklık")
    fig3, info_text3 = plot_last_day_volatility(cv_data, window=window_size)
    st.info(info_text3)
    st.plotly_chart(fig3, use_container_width=True)

if page == "Tüm Analizler" or page == "Momentum Analizi":
    st.header("Momentum Analizi")
    fig4, info_text4 = plot_momentum_analysis(all_data, periods=window_size)
    st.info(info_text4)
    st.plotly_chart(fig4, use_container_width=True)

if page == "Tüm Analizler" or page == "Oynaklık vs Getiri":
    st.header("Oynaklık vs Getiri İlişkisi")
    fig5, info_text5 = plot_volatility_vs_return(cv_data, all_data, periods=window_size)
    st.info(info_text5)
    st.plotly_chart(fig5, use_container_width=True)

if page == "Tüm Analizler" or page == "Risk-Getiri Analizi":
    st.header("Risk-Getiri Performansı")
    fig6, info_text6 = plot_sharpe_ratio(cv_data, all_data, periods=window_size)
    st.info(info_text6)
    st.plotly_chart(fig6, use_container_width=True)

if page == "Tüm Analizler" or page == "Zirveden Uzaklık":
    st.header("Zirveden Uzaklık Analizi")
    
    # Hisse seçimi
    selected_stock = st.selectbox(
        "Hisse Senedi Seçin", 
        options=all_data.columns,
        format_func=lambda x: x.replace('.IS', '')
    )
    
    fig7, info_text7 = plot_price_drawdown(all_data, selected_stock)
    st.info(info_text7)
    st.plotly_chart(fig7, use_container_width=True)

# Footer
st.markdown("---")
st.caption("© 2024 • Borsa Oynaklık Analizi") 