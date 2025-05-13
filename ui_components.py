import streamlit as st
import os

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

# Sidebar UI
def create_sidebar(DEFAULT_TICKERS):
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
        selected_tickers = DEFAULT_TICKERS
    else:
        custom_tickers = st.sidebar.text_area(
            "Özel hisse kodları",
            value="\n".join(DEFAULT_TICKERS[:5]),
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