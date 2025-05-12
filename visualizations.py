import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def format_date(date):
    """Tarihi 'gün/ay/yıl' formatına dönüştürür"""
    return date.strftime('%d/%m/%Y')

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
    
    title_text = f"En Oynak {top_n} Hisse (Varyasyon Katsayısı) - {format_date(first_date)} ile {format_date(last_date)} arası"
    
    fig = px.line(
        df_plot,
        x=df_plot.index,
        y=df_plot.columns,
        title=title_text
    )
    
    fig.update_layout(
        xaxis_title="Tarih",
        yaxis_title="Std / Ortalama",
        legend_title="Hisseler",
        hovermode="x unified"
    )
    
    return fig, info_text

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
    
    # Transpose eden heatmap (Sıralanmış hisseleri kullan)
    fig = px.imshow(
        sorted_cv_data.T,
        color_continuous_scale='Viridis',
        labels=dict(x="Tarih", y="Hisseler", color="Varyasyon Katsayısı"),
        title=f"Göreli Oynaklık - Isı Haritası - {format_date(first_date)} ile {format_date(last_date)} arası"
    )
    
    fig.update_layout(height=600)
    
    return fig, info_text

def plot_last_day_volatility(cv_data, window=20):
    """Son gün oynaklık için bar grafiği"""
    last_date = cv_data.index[-1]
    cv_last = cv_data.loc[last_date].sort_values(ascending=False)
    
    info_text = (
        f"ℹ️ **Son Gün Oynaklık:** Son tarih için her hissenin son {window} günlük "
        f"oynaklık değerlerini gösterir. Değer, ilgili dönemdeki fiyatların standart sapmasının "
        f"ortalamaya bölünmesiyle hesaplanır."
    )
    
    fig = px.bar(
        x=cv_last.index,
        y=cv_last.values,
        title=f"{format_date(last_date)} İtibarıyla {window} Günlük Varyasyon Katsayıları",
        labels={'x': 'Hisseler', 'y': 'Std / Ortalama'}
    )
    
    return fig, info_text

def plot_momentum_analysis(all_data, periods=20):
    """Momentum analizi (20 günlük getiri)"""
    momentum = all_data.pct_change(periods=periods).iloc[-1].sort_values(ascending=False)
    
    first_date = all_data.index[-periods]
    last_date = all_data.index[-1]
    
    info_text = (
        f"ℹ️ **Momentum Analizi:** Her hissenin son {periods} günlük yüzde değişimini gösterir. "
        f"Formül: (Son Fiyat - {periods} Gün Önceki Fiyat) / {periods} Gün Önceki Fiyat × 100. "
        f"Yeşil pozitif, kırmızı negatif getiriyi gösterir."
    )
    
    fig = px.bar(
        x=momentum.index,
        y=momentum.values * 100,  # Yüzde olarak göster
        title=f"En Fazla Yükselen/Düşen Hisseler - {format_date(first_date)} ile {format_date(last_date)} arası",
        labels={'x': 'Hisseler', 'y': 'Getiri (%)'},
        color=momentum.values,
        color_continuous_scale=['red', 'green']
    )
    
    return fig, info_text

def plot_volatility_vs_return(cv_data, all_data, periods=20):
    """Oynaklık ve getiri ilişkisi için scatter plot"""
    last_date = cv_data.index[-1]
    cv_last = cv_data.loc[last_date]
    returns_last_n = all_data.pct_change(periods=periods).iloc[-1]
    
    first_date = all_data.index[-periods]
    
    info_text = (
        f"ℹ️ **Oynaklık vs Getiri:** X ekseni her hissenin son oynaklık değerini, Y ekseni ise "
        f"son {periods} günlük yüzde getirisini gösterir. Grafiğin sağ üst kısmı yüksek getiri ve "
        f"yüksek oynaklığı, sol üst kısmı ise düşük oynaklık ve yüksek getiriyi (ideal durum) ifade eder."
    )
    
    # İki seriyi birleştirerek dataframe oluştur
    df = pd.DataFrame({
        'Oynaklık': cv_last,
        'Getiri (%)': returns_last_n * 100
    })
    df['Hisse'] = df.index
    
    fig = px.scatter(
        df, 
        x='Oynaklık', 
        y='Getiri (%)',
        text='Hisse',
        title=f"Oynaklık vs Getiri - {format_date(first_date)} ile {format_date(last_date)} arası",
        color='Getiri (%)',
        color_continuous_scale=['red', 'green']
    )
    
    fig.update_traces(textposition='top center')
    
    return fig, info_text

def plot_sharpe_ratio(cv_data, all_data, periods=20):
    """Sharpe benzeri oran (Getiri / Oynaklık)"""
    last_date = cv_data.index[-1]
    cv_last = cv_data.loc[last_date]
    returns_last_n = all_data.pct_change(periods=periods).iloc[-1]
    
    first_date = all_data.index[-periods]
    
    info_text = (
        f"ℹ️ **Risk-Getiri Oranı:** Her hissenin son {periods} günlük getirisinin, "
        f"oynaklığına bölünmesiyle elde edilir. Bu oran, birim risk başına elde edilen getiriyi gösterir. "
        f"Yüksek değerler, risk göz önüne alındığında daha iyi performans gösterenleri belirtir."
    )
    
    # Sharpe benzeri oran
    sharpe_like = (returns_last_n / cv_last).sort_values(ascending=False)
    
    fig = px.bar(
        x=sharpe_like.index,
        y=sharpe_like.values,
        title=f"Riske Göre Düzeltilmiş Performans (Getiri / Oynaklık) - {format_date(first_date)} ile {format_date(last_date)} arası",
        labels={'x': 'Hisseler', 'y': 'Oran'},
        color=sharpe_like.values,
        color_continuous_scale=['red', 'green']
    )
    
    return fig, info_text 