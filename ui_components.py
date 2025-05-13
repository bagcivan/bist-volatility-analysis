import streamlit as st
import os
from constants import DEFAULT_TICKERS
from html_components import HtmlComponent

# CSS Stilleri
def load_css():
    """
    CSS stillerini harici dosyadan yükler
    """
    css_file_path = "static/styles.css"
    
    # Dosyanın var olup olmadığını kontrol et
    if os.path.exists(css_file_path):
        with open(css_file_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.error(f"CSS dosyası bulunamadı: {css_file_path}")

# UI Bileşenleri
class ProgressBar(HtmlComponent):
    """İlerleme çubuğu bileşeni"""
    
    @staticmethod
    def create(positive_count, negative_count, unchanged_count, total_stocks):
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

class MetricCard(HtmlComponent):
    """Metrik kartı bileşeni"""
    
    @staticmethod
    def create(label, value, subtitle, is_percentage=False, value_class=None):
        """Metrik kartı HTML'i oluşturur"""
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

# Sidebar UI
def create_sidebar(default_tickers=None):
    """Sidebar kullanıcı arayüzünü oluşturur
    
    Args:
        default_tickers: Varsayılan hisse kodları listesi, None ise constants.DEFAULT_TICKERS kullanılır
        
    Returns:
        Tuple: (data_days, window_size, top_n, selected_tickers, refresh_btn, page)
    """
    if default_tickers is None:
        default_tickers = DEFAULT_TICKERS
        
    # Sidebar için zarif logo ve başlık
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h1 class="sidebar-title">📊 Borsa Analizi</h1>
        <p class="sidebar-description">BIST Hisseleri için Analiz Aracı</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar ayarları
    st.sidebar.markdown('<p class="sidebar-subtitle">Veri Parametreleri</p>', unsafe_allow_html=True)

    col1, col2 = st.sidebar.columns(2)
    with col1:
        data_days = st.slider("Veri Günü", 30, 180, 40, key="data_days")
    with col2:
        window_size = st.slider("Pencere (Gün)", 10, 30, 20, key="window_size")

    top_n = st.sidebar.slider("Gösterilecek Hisse", 3, 10, 5, key="top_n")
    
    # Separator
    st.sidebar.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.sidebar.markdown('<p class="sidebar-subtitle">Hisse Seçimi</p>', unsafe_allow_html=True)

    # Hisse seçimi
    use_default = st.sidebar.checkbox("BIST-30 Hisseleri", value=True)

    if use_default:
        selected_tickers = default_tickers
    else:
        custom_tickers = st.sidebar.text_area(
            "Özel hisse kodları",
            value="\n".join(default_tickers[:5]),
            help="Her satıra bir hisse kodu girin, örneğin: THYAO.IS",
            height=120
        )
        selected_tickers = [t.strip() for t in custom_tickers.split("\n") if t.strip()]

    # Veri yenileme butonu
    st.sidebar.markdown('<div class="button-container">', unsafe_allow_html=True)
    refresh_btn = st.sidebar.button("🔄 Verileri Yenile")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Sayfa seçimi (artık tek sayfa var)
    page = "📊 Piyasa Özeti"  # Her zaman Piyasa Özeti'ni göster
    
    # Sidebar footer
    st.sidebar.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div class="footer">
        📈 BIST Analiz Aracı <br>
        v1.0.0
    </div>
    """, unsafe_allow_html=True)
    
    return data_days, window_size, top_n, selected_tickers, refresh_btn, page 