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
    format_last_update,
    LastUpdateInfo,
    memoize
)
import datetime

# Önbelleğe alınmış fonksiyonlar
@memoize
def get_daily_change(all_data):
    """Günlük değişim hesapla"""
    return calculate_percent_change(all_data)

class TabManager:
    """Tab oluşturma ve yönetme işlemleri için yardımcı sınıf"""
    
    def __init__(self, all_data, cv_data, window_size, top_n):
        """Gerekli parametrelerle başlatıcı fonksiyon"""
        self.all_data = all_data
        self.cv_data = cv_data
        self.window_size = window_size
        self.top_n = top_n
        self.daily_change = get_daily_change(all_data)
        
        # Tab konfigürasyonları
        self.tabs_config = [
            {"id": 0, "name": "📊 Piyasa Özeti", "handler": self.handle_market_summary},
            {"id": 1, "name": "📈 En Oynak Hisseler", "handler": self.handle_volatile_stocks},
            {"id": 2, "name": "🔥 Isı Haritası", "handler": self.handle_heatmap},
            {"id": 3, "name": "📉 Son Gün Oynaklık", "handler": self.handle_last_day_volatility},
            {"id": 4, "name": "📈 Getiri Analizi", "handler": self.handle_return_analysis},
            {"id": 5, "name": "⚖️ Oynaklık vs Getiri", "handler": self.handle_volatility_vs_return},
            {"id": 6, "name": "📋 Risk-Getiri Analizi", "handler": self.handle_sharpe_ratio},
            {"id": 7, "name": "🏔️ Zirveden Uzaklık", "handler": self.handle_price_drawdown}
        ]
    
    def create_tabs(self):
        """Sekmeleri oluştur ve yönet"""
        tab_names = [tab["name"] for tab in self.tabs_config]
        tabs = st.tabs(tab_names)
        
        # Tab içeriklerini işle
        for tab_config in self.tabs_config:
            tab_id = tab_config["id"]
            with tabs[tab_id]:
                tab_config["handler"]()
    
    def show_figure_with_info(self, fig, info_text):
        """Figürü ve bilgi metnini standart bir biçimde göster"""
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': 'hover'})
        with st.expander("ℹ️ Bilgi"):
            st.markdown(info_text, unsafe_allow_html=True)
    
    # Tab içerik işleyicileri
    def handle_market_summary(self):
        """Piyasa Özeti Sekmesi işleyicisi"""
        info_text0 = plot_market_summary(self.all_data, self.cv_data)
        with st.expander("ℹ️ Bilgi"):
            st.markdown(info_text0, unsafe_allow_html=True)
    
    def handle_volatile_stocks(self):
        """En Oynak Hisseler Sekmesi işleyicisi"""
        fig1, info_text1 = plot_top_volatile_stocks(self.cv_data, top_n=self.top_n)
        self.show_figure_with_info(fig1, info_text1)
        
        # Detaylı bilgi tablosu ekle
        st.markdown("#### En Oynak Hisseler Detayı", unsafe_allow_html=True)
        
        last_date = self.cv_data.index[-1]
        top_stocks = self.cv_data.loc[last_date].sort_values(ascending=False).head(self.top_n)
        
        # Hisselerin detaylı bilgileri
        stocks_detail = pd.DataFrame({
            'Hisse': [clean_ticker(stock) for stock in top_stocks.index],
            'Varyasyon Katsayısı': top_stocks.values.round(4),
            'Son Fiyat': [self.all_data[stock].iloc[-1] for stock in top_stocks.index],
            'Değişim (%)': [self.daily_change[stock] for stock in top_stocks.index]
        })
        
        st.dataframe(stocks_detail, use_container_width=True, hide_index=True)
    
    def handle_heatmap(self):
        """Isı Haritası Sekmesi işleyicisi"""
        fig2, info_text2 = plot_volatility_heatmap(self.cv_data)
        self.show_figure_with_info(fig2, info_text2)
    
    def handle_last_day_volatility(self):
        """Son Gün Oynaklık Sekmesi işleyicisi"""
        fig3, info_text3 = plot_last_day_volatility(self.cv_data, window=self.window_size)
        self.show_figure_with_info(fig3, info_text3)
    
    def handle_return_analysis(self):
        """Getiri Analizi Sekmesi işleyicisi"""
        period_options = {"1 Hafta": 5, "2 Hafta": 10, "1 Ay": 20, "3 Ay": 60}
        selected_period = st.selectbox(
            "Karşılaştırma Periyodu:",
            options=list(period_options.keys())
        )
        
        fig4, info_text4 = plot_return_analysis(self.all_data, periods=period_options[selected_period])
        self.show_figure_with_info(fig4, info_text4)
    
    def handle_volatility_vs_return(self):
        """Oynaklık vs Getiri Sekmesi işleyicisi"""
        fig5, info_text5 = plot_volatility_vs_return(self.cv_data, self.all_data, periods=self.window_size)
        self.show_figure_with_info(fig5, info_text5)
    
    def handle_sharpe_ratio(self):
        """Risk-Getiri Analizi Sekmesi işleyicisi"""
        fig6, info_text6 = plot_sharpe_ratio(self.cv_data, self.all_data, periods=self.window_size)
        self.show_figure_with_info(fig6, info_text6)
    
    def handle_price_drawdown(self):
        """Zirveden Uzaklık Sekmesi işleyicisi"""
        # Hisse seçimi
        selected_stock = st.selectbox(
            "Hisse Senedi", 
            options=self.all_data.columns,
            format_func=clean_ticker
        )
        
        fig7, info_text7 = plot_price_drawdown(self.all_data, selected_stock)
        self.show_figure_with_info(fig7, info_text7)

def show_market_overview(all_data, cv_data, window_size, top_n):
    """Piyasa genel görünümünü göster"""
    # Tab yöneticisini başlat ve tabları göster
    tab_manager = TabManager(all_data, cv_data, window_size, top_n)
    tab_manager.create_tabs()

# Ana içerik yönetimi
def render_page(page, all_data, cv_data, window_size, top_n):
    """Sayfayı oluştur ve görüntüle"""
    # Sayfa başlığı ve içerik
    page_title = extract_page_title(page)
    
    # Son veri tarihini göster
    if not all_data.empty:
        last_date = all_data.index[-1]
        current_time = datetime.datetime.now()
        st.markdown(LastUpdateInfo.create(last_date, current_time), unsafe_allow_html=True)
    
    # Ana sayfa başlığı
    st.markdown(f'<h1 class="main-header">{page_title}</h1>', unsafe_allow_html=True)
    
    # İçeriği göster
    show_market_overview(all_data, cv_data, window_size, top_n) 