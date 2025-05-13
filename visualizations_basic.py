import plotly.express as px
from theme_constants import COLOR_SCALE
from utils import (
    format_date, 
    apply_figure_template, 
    clean_ticker, 
    clean_ticker_series,
    calculate_percent_change,
    format_gains,
    format_losses,
    generate_market_progress_bar,
    generate_metric_card,
    create_styled_dataframe
)
import streamlit as st
import pandas as pd

@apply_figure_template
def plot_top_volatile_stocks(cv_data, top_n=5):
    """En oynak hisseleri plotly ile çizdir"""
    last_date = cv_data.index[-1]
    first_date = cv_data.index[0]
    top_stocks = cv_data.loc[last_date].sort_values(ascending=False).head(top_n)
    
    # Seçilen hisselerin zaman serileri
    df_plot = cv_data[top_stocks.index]
    
    info_text = (
        "ℹ️ **Varyasyon Katsayısı:** Fiyatların standart sapmasının ortalamaya bölünmesiyle "
        "hesaplanır. Yüksek değerler daha oynak hisseleri gösterir."
    )
    
    title_text = f"En Oynak {top_n} Hisse - {format_date(first_date)} ile {format_date(last_date)} arası"
    
    fig = px.line(
        df_plot,
        x=df_plot.index,
        y=df_plot.columns,
        title=title_text,
        color_discrete_sequence=COLOR_SCALE,
        labels={"value": "Varyasyon Katsayısı", "variable": "Hisse", "x": "Tarih"}
    )
    
    fig.update_traces(
        line=dict(width=2),
        hovertemplate='<b>%{y:.4f}</b><br>%{x|%d.%m.%Y}<extra>%{fullData.name}</extra>'
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
    
    # Transpose eden heatmap (Sıralanmış hisseleri kullan)
    fig = px.imshow(
        sorted_cv_data.T,
        color_continuous_scale='Viridis',
        labels=dict(x="Tarih", y="Hisseler", color="Varyasyon Katsayısı"),
        title=f"Oynaklık Isı Haritası - {format_date(first_date)} ile {format_date(last_date)} arası",
        y=clean_labels
    )
    
    fig.update_layout(
        height=650,
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(0, len(sorted_cv_data.index), max(1, len(sorted_cv_data.index)//8))),
            ticktext=[dt.strftime('%d.%m.%Y') for dt in sorted_cv_data.index[::max(1, len(sorted_cv_data.index)//8)]]
        ),
        coloraxis=dict(
            colorbar=dict(
                title="Varyasyon<br>Katsayısı",
                titleside="right",
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
    
    # Hisse kodlarını kısalt - clean_ticker_series kullanarak
    hisseler = clean_ticker_series(cv_last.index)
    degerler = cv_last.values
    
    fig = px.bar(
        x=hisseler,
        y=degerler,
        title=f"{format_date(last_date)} İtibarıyla {window} Günlük Varyasyon Katsayıları",
        labels={'x': 'Hisseler', 'y': 'Varyasyon Katsayısı'},
        color=degerler,
        color_continuous_scale='Viridis',
        text=[f"{val:.4f}" for val in degerler]
    )
    
    fig.update_traces(
        textposition='outside',
        textfont=dict(size=9, color="#333"),
        hovertemplate='<b>%{x}</b>: %{y:.4f}<extra></extra>'
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
    progress_bar_html = generate_market_progress_bar(
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
            generate_metric_card(
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
            generate_metric_card(
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
            generate_metric_card(
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
            generate_metric_card(
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
        title_html, df_html = create_styled_dataframe(
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
        title_html, df_html = create_styled_dataframe(
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
        f"En yüksek getiri: **{top_gainers.index[0].replace('.IS', '')}** (%{top_gainers.values[0]:.2f})\n\n"
        f"En düşük getiri: **{top_losers.index[0].replace('.IS', '')}** (%{top_losers.values[0]:.2f})"
    )
    
    return info_text

