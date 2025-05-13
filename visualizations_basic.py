import plotly.express as px
from constants import (
    COLOR_SCALE, UP_COLOR, DOWN_COLOR, NEUTRAL_COLOR, 
    HEATMAP_COLOR_SCALE, TEXT_FONT_SIZE, HOVER_TEXT_COLOR,
    LINE_WIDTH, GRAPH_HEIGHT, HEATMAP_HEIGHT
)
from formatters import (
    format_date,
    format_gains,
    format_losses,
    clean_ticker,
    clean_ticker_series
)
from visualization_helpers import apply_figure_template, PlotHelpers
from data_services import calculate_percent_change
from ui_components import (
    ProgressBar,
    MetricCard
)
from html_components import (
    StyledDataFrame
)
import streamlit as st
import pandas as pd

@apply_figure_template
def plot_top_volatile_stocks(cv_data, top_n=5):
    """En oynak hisseleri plotly ile çizdir"""
    last_date = cv_data.index[-1]
    first_date = cv_data.index[0]
    
    # Son tarih için en oynak hisseleri bulalım
    top_stocks = cv_data.loc[last_date].sort_values(ascending=False).head(top_n)
    
    # Seçilen hisselerin zaman serileri
    df_plot = cv_data[top_stocks.index]
    
    info_text = (
        "ℹ️ **Varyasyon Katsayısı:** Fiyatların standart sapmasının ortalamaya bölünmesiyle "
        "hesaplanır. Yüksek değerler daha oynak hisseleri gösterir."
    )
    
    # Başlık oluştur
    title = PlotHelpers.get_date_range_title(
        first_date, last_date, f"En Oynak {top_n} Hisse"
    )
    
    # Çizgi grafiği oluştur - PlotHelpers kullanarak
    fig = PlotHelpers.create_line_chart(
        df=df_plot,
        title=title,
        y_label="Varyasyon Katsayısı",
        hover_precision=4
    )
    
    return fig, info_text

@apply_figure_template
def plot_volatility_heatmap(cv_data):
    """Oynaklık ısı haritasını plotly ile çizdir"""
    # Hisselerin ortalama oynaklığını hesapla ve sırala
    avg_volatility = cv_data.mean().sort_values(ascending=False)
    # Sıralanmış hisseleri kullanarak veriyi yeniden düzenle
    sorted_cv_data = cv_data[avg_volatility.index]
    
    first_date = cv_data.index[0]
    last_date = cv_data.index[-1]
    
    info_text = (
        "ℹ️ **Isı Haritası:** Her kare, ilgili tarihteki hissenin oynaklık değerini (varyasyon katsayısı) "
        "gösterir. Koyu renkler daha yüksek oynaklığı ifade eder. Hisseler ortalama oynaklık değerine "
        "göre yukarıdan aşağıya doğru sıralanmıştır."
    )
    
    # Hisse kodlarını kısalt (IS uzantısını kaldır) - clean_ticker kullanarak
    clean_labels = [clean_ticker(label) for label in sorted_cv_data.columns]
    
    # Başlık oluştur - PlotHelpers kullanarak
    title = PlotHelpers.get_date_range_title(
        first_date, last_date, "Oynaklık Isı Haritası"
    )
    
    # Transpose eden heatmap (Sıralanmış hisseleri kullan)
    fig = px.imshow(
        sorted_cv_data.T,
        color_continuous_scale=HEATMAP_COLOR_SCALE,
        labels=dict(x="Tarih", y="Hisseler", color="Varyasyon Katsayısı"),
        title=title,
        y=clean_labels
    )
    
    fig.update_layout(
        height=HEATMAP_HEIGHT,
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(0, len(sorted_cv_data.index), max(1, len(sorted_cv_data.index)//8))),
            ticktext=[dt.strftime('%d.%m.%Y') for dt in sorted_cv_data.index[::max(1, len(sorted_cv_data.index)//8)]]
        ),
        coloraxis=dict(
            colorbar=dict(
                title=dict(
                    text="Varyasyon<br>Katsayısı",
                    side="right"
                ),
                ticks="outside"
            )
        )
    )
    
    return fig, info_text

@apply_figure_template
def plot_last_day_volatility(cv_data, window=20):
    """Son gün oynaklık için bar grafiği"""
    last_date = cv_data.index[-1]
    cv_last = cv_data.loc[last_date].sort_values(ascending=False)
    
    info_text = (
        f"ℹ️ **Son Gün Oynaklık:** Son tarih için her hissenin son {window} günlük "
        f"oynaklık değerlerini gösterir. Değer, ilgili dönemdeki fiyatların standart sapmasının "
        f"ortalamaya bölünmesiyle hesaplanır."
    )
    
    # Hisse kodlarını temizle ve verileri hazırla
    hisseler, degerler = PlotHelpers.prepare_stock_data(cv_last)
    
    # Bar grafiği oluştur - PlotHelpers kullanarak
    title = f"{format_date(last_date)} İtibarıyla {window} Günlük Varyasyon Katsayıları"
    
    fig = PlotHelpers.create_bar_chart(
        x_data=hisseler,
        y_data=degerler,
        title=title,
        y_label='Varyasyon Katsayısı',
        color_scale=HEATMAP_COLOR_SCALE,
        precision=4
    )
    
    return fig, info_text

def plot_market_summary(all_data, cv_data):
    """Piyasa özeti sekmesi için tüm içeriği oluşturur
    
    Args:
        all_data: Hisse senedi fiyat verileri DataFrame
        cv_data: Varyasyon katsayısı DataFrame
    
    Returns:
        info_text: Piyasa özetine dair bilgi metni
    """
    # Günlük yükseliş/düşüş istatistikleri hesaplama
    daily_change = calculate_percent_change(all_data)
    positive_count = (daily_change > 0).sum()
    negative_count = (daily_change < 0).sum()
    unchanged_count = (daily_change == 0).sum()
    total_stocks = len(daily_change)
    
    # Yükselen/düşen hisseleri yatay stack bar olarak göster
    # Yatay stack bar için HTML oluştur
    progress_bar_html = ProgressBar.create(
        positive_count, negative_count, unchanged_count, total_stocks
    )
    st.markdown(progress_bar_html, unsafe_allow_html=True)
    
    # Metrik kartları için satır oluştur
    metric_cols = st.columns(4)
    
    # En büyük yükseliş
    with metric_cols[0]:
        max_gain = daily_change.max()
        max_gain_stock = clean_ticker(daily_change.idxmax())
        st.markdown(
            MetricCard.create(
                "En Büyük Yükseliş", 
                max_gain, 
                max_gain_stock, 
                is_percentage=True, 
                value_class="positive"
            ), 
            unsafe_allow_html=True
        )
    
    # En büyük düşüş    
    with metric_cols[1]:
        max_loss = daily_change.min()
        max_loss_stock = clean_ticker(daily_change.idxmin())
        st.markdown(
            MetricCard.create(
                "En Büyük Düşüş", 
                max_loss, 
                max_loss_stock, 
                is_percentage=True, 
                value_class="negative"
            ), 
            unsafe_allow_html=True
        )
    
    # Ortalama değişim    
    with metric_cols[2]:
        avg_change = daily_change.mean()
        direction = "Yükseliş" if avg_change > 0 else "Düşüş"
        st.markdown(
            MetricCard.create(
                "Ortalama Değişim", 
                avg_change, 
                f"Genel Eğilim: {direction}", 
                is_percentage=True, 
                value_class="positive" if avg_change > 0 else "negative"
            ), 
            unsafe_allow_html=True
        )
    
    # En oynak hisse
    with metric_cols[3]:
        max_vol = cv_data.iloc[-1].max()
        max_vol_stock = clean_ticker(cv_data.iloc[-1].idxmax())
        st.markdown(
            MetricCard.create(
                "En Oynak Hisse", 
                max_vol_stock, 
                f"Varyasyon: {max_vol:.4f}", 
                is_percentage=False
            ), 
            unsafe_allow_html=True
        )
    
    # Top yükselenler ve düşenler - daha kompakt
    st.markdown('<h3 class="sub-header">En Çok Yükselenler ve Düşenler</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Yüzde değişim - zaten hesaplanmış olan daily_change'i kullan
    top_gainers = daily_change.sort_values(ascending=False).head(5)
    top_losers = daily_change.sort_values().head(5)
    
    with col1:
        # Doğrudan clean_ticker_series kullanarak
        gainers_df = pd.DataFrame({
            'Hisse': clean_ticker_series(top_gainers.index),
            'Getiri (%)': top_gainers.values.round(2)
        })
        
        # Styled dataframe oluştur
        title_html, df_html = StyledDataFrame.create(
            gainers_df, 
            "📈 En Çok Yükselenler", 
            "positive", 
            format_gains
        )
        
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(df_html, unsafe_allow_html=True)
    
    with col2:
        # Doğrudan clean_ticker_series kullanarak
        losers_df = pd.DataFrame({
            'Hisse': clean_ticker_series(top_losers.index),
            'Getiri (%)': top_losers.values.round(2)
        })
        
        # Styled dataframe oluştur
        title_html, df_html = StyledDataFrame.create(
            losers_df, 
            "📉 En Çok Düşenler", 
            "negative", 
            format_losses
        )
        
        st.markdown(title_html, unsafe_allow_html=True)
        st.markdown(df_html, unsafe_allow_html=True)
    
    # Bilgi metni
    info_text = (
        f"ℹ️ **Piyasa Özeti:** Seçilen hisseler arasında {positive_count} adet yükselen (%{positive_count/total_stocks*100:.1f}), "
        f"{negative_count} adet düşen (%{negative_count/total_stocks*100:.1f}) ve "
        f"{unchanged_count} adet değişmeyen (%{unchanged_count/total_stocks*100:.1f}) hisse bulunmaktadır.\n\n"
        f"En yüksek getiri: **{clean_ticker(top_gainers.index[0])}** (%{top_gainers.values[0]:.2f})\n\n"
        f"En düşük getiri: **{clean_ticker(top_losers.index[0])}** (%{top_losers.values[0]:.2f})"
    )
    
    return info_text

