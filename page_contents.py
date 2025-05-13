import streamlit as st
import pandas as pd
from visualizations_basic import (
    plot_top_volatile_stocks,
    plot_volatility_heatmap,
    plot_last_day_volatility,
    plot_market_summary
)
from visualizations_advanced import (
    plot_return_analysis,
    plot_volatility_vs_return,
    plot_sharpe_ratio,
    plot_price_drawdown
)
from utils import (
    clean_ticker, 
    calculate_percent_change,
    extract_page_title,
    format_last_update
)
import datetime

def show_market_overview(all_data, cv_data, window_size, top_n):
    # Günlük yükseliş/düşüş istatistikleri hesaplama
    daily_change = calculate_percent_change(all_data)
    
    # Tab konfigürasyonları
    tabs_config = [
        {"id": 0, "name": "📊 Piyasa Özeti", "has_figure": False},
        {"id": 1, "name": "📈 En Oynak Hisseler", "has_figure": True, "function": plot_top_volatile_stocks, "args": {"cv_data": cv_data, "top_n": top_n}},
        {"id": 2, "name": "🔥 Isı Haritası", "has_figure": True, "function": plot_volatility_heatmap, "args": {"cv_data": cv_data}},
        {"id": 3, "name": "📉 Son Gün Oynaklık", "has_figure": True, "function": plot_last_day_volatility, "args": {"cv_data": cv_data, "window": window_size}},
        {"id": 4, "name": "📈 Getiri Analizi", "has_figure": True, "function": None, "has_custom_config": True},
        {"id": 5, "name": "⚖️ Oynaklık vs Getiri", "has_figure": True, "function": plot_volatility_vs_return, "args": {"cv_data": cv_data, "all_data": all_data, "periods": window_size}},
        {"id": 6, "name": "📋 Risk-Getiri Analizi", "has_figure": True, "function": plot_sharpe_ratio, "args": {"cv_data": cv_data, "all_data": all_data, "periods": window_size}},
        {"id": 7, "name": "🏔️ Zirveden Uzaklık", "has_figure": True, "function": None, "has_custom_config": True}
    ]
    
    # Sekmeleri oluştur
    tab_names = [tab["name"] for tab in tabs_config]
    tabs = st.tabs(tab_names)
    
    # Tab içeriklerini oluştur
    for tab_config in tabs_config:
        tab_id = tab_config["id"]
        
        with tabs[tab_id]:
            # Özel konfigürasyonlu tablar
            if tab_id == 0:  # Piyasa Özeti Sekmesi
                info_text0 = plot_market_summary(all_data, cv_data)
                with st.expander("ℹ️ Bilgi"):
                    st.markdown(info_text0, unsafe_allow_html=True)
                
            elif tab_id == 4:  # Getiri Analizi Sekmesi
                period_options = {"1 Hafta": 5, "2 Hafta": 10, "1 Ay": 20, "3 Ay": 60}
                selected_period = st.selectbox(
                    "Karşılaştırma Periyodu:",
                    options=list(period_options.keys())
                )
                
                fig4, info_text4 = plot_return_analysis(all_data, periods=period_options[selected_period])
                st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': 'hover'})
                with st.expander("ℹ️ Bilgi"):
                    st.markdown(info_text4, unsafe_allow_html=True)
                
            elif tab_id == 7:  # Zirveden Uzaklık Sekmesi
                # Hisse seçimi
                selected_stock = st.selectbox(
                    "Hisse Senedi", 
                    options=all_data.columns,
                    format_func=clean_ticker
                )
                
                fig7, info_text7 = plot_price_drawdown(all_data, selected_stock)
                st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': 'hover'})
                with st.expander("ℹ️ Bilgi"):
                    st.markdown(info_text7, unsafe_allow_html=True)
            
            # Standart grafik tabları
            elif tab_config["has_figure"] and not tab_config.get("has_custom_config", False):
                fig, info_text = tab_config["function"](**tab_config["args"])
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': 'hover'})
                with st.expander("ℹ️ Bilgi"):
                    st.markdown(info_text, unsafe_allow_html=True)
                
                # En Oynak Hisseler için ek içerik
                if tab_id == 1:
                    st.markdown("#### En Oynak Hisseler Detayı", unsafe_allow_html=True)
                    
                    last_date = cv_data.index[-1]
                    top_stocks = cv_data.loc[last_date].sort_values(ascending=False).head(top_n)
                    
                    # Hisselerin detaylı bilgileri
                    stocks_detail = pd.DataFrame({
                        'Hisse': [clean_ticker(stock) for stock in top_stocks.index],
                        'Varyasyon Katsayısı': top_stocks.values.round(4),
                        'Son Fiyat': [all_data[stock].iloc[-1] for stock in top_stocks.index],
                        'Değişim (%)': [daily_change[stock] for stock in top_stocks.index]
                    })
                    
                    st.dataframe(stocks_detail, use_container_width=True, hide_index=None)

# Ana içerik yönetimi
def render_page(page, all_data, cv_data, window_size, top_n):
    # Sayfa başlığı ve içerik
    page_title = extract_page_title(page)
    
    # Son veri tarihini göster
    if not all_data.empty:
        last_date = all_data.index[-1]
        current_time = datetime.datetime.now()
        st.markdown(format_last_update(last_date, current_time), unsafe_allow_html=True)
    
    # Ana sayfa başlığı
    st.markdown(f'<h1 class="main-header">{page_title}</h1>', unsafe_allow_html=True)
    
    # İçeriği göster
    show_market_overview(all_data, cv_data, window_size, top_n) 