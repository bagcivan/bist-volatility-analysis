import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from theme_constants import (
    UP_COLOR, DOWN_COLOR, NEUTRAL_COLOR, 
    RETURN_COLOR_SCALE, HEATMAP_COLOR_SCALE,
    TEXT_FONT_SIZE, HOVER_TEXT_COLOR, 
    LINE_WIDTH, GRAPH_HEIGHT,
    BAR_TEXT_FORMAT, PERCENTAGE_FORMAT
)
from utils import format_date, apply_figure_template, clean_ticker, clean_ticker_series

@apply_figure_template
def plot_return_analysis(all_data, periods=20):
    """Getiri analizi (20 günlük getiri)"""
    momentum = all_data.pct_change(periods=periods).iloc[-1].sort_values(ascending=False)
    
    first_date = all_data.index[-periods]
    last_date = all_data.index[-1]
    
    info_text = (
        f"ℹ️ **Getiri Analizi:** Her hissenin son {periods} günlük yüzde değişimini gösterir. "
        f"Formül: (Son Fiyat - {periods} Gün Önceki Fiyat) / {periods} Gün Önceki Fiyat × 100. "
        f"Yeşil pozitif, kırmızı negatif getiriyi gösterir."
    )
    
    # Hisse kodlarını kısalt
    hisseler = clean_ticker_series(momentum.index)
    degerler = momentum.values * 100  # Yüzde olarak göster
    
    # Renk skalası - theme_constants'tan al
    fig = px.bar(
        x=hisseler,
        y=degerler,
        title=f"En Fazla Yükselen/Düşen Hisseler - {format_date(first_date)} ile {format_date(last_date)} arası",
        labels={'x': 'Hisseler', 'y': 'Getiri (%)'},
        color=degerler,
        color_continuous_scale=RETURN_COLOR_SCALE,
        text=[PERCENTAGE_FORMAT.format(val) for val in degerler]
    )
    
    fig.update_traces(
        textposition='outside',
        textfont=dict(size=TEXT_FONT_SIZE, color=HOVER_TEXT_COLOR),
        hovertemplate='<b>%{x}</b>: %{y:.2f}%<extra></extra>'
    )
    
    # Y ekseni için 0 çizgisi ekle
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(hisseler)-0.5,
        y0=0,
        y1=0,
        line=dict(color="#aaaaaa", width=1, dash="dot")
    )
    
    return fig, info_text

@apply_figure_template
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
    df['Hisse'] = clean_ticker_series(df.index)
    
    # Renk skalası - theme_constants'tan al
    fig = px.scatter(
        df, 
        x='Oynaklık', 
        y='Getiri (%)',
        text='Hisse',
        title=f"Oynaklık vs Getiri - {format_date(first_date)} ile {format_date(last_date)} arası",
        color='Getiri (%)',
        size=abs(df['Getiri (%)']).clip(1, 20),  # Değişim miktarına göre boyutlandır
        color_continuous_scale=RETURN_COLOR_SCALE,
        hover_data={
            'Oynaklık': ':.4f',
            'Getiri (%)': ':.2f',
            'Hisse': True
        }
    )
    
    fig.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=1, color='#DDD')),
        textfont=dict(size=TEXT_FONT_SIZE, color=HOVER_TEXT_COLOR),
    )
    
    # Eksen çizgileri
    fig.add_shape(
        type="line",
        x0=0,
        x1=df['Oynaklık'].max() * 1.1,
        y0=0,
        y1=0,
        line=dict(color="#aaaaaa", width=1, dash="dot")
    )
    
    return fig, info_text

@apply_figure_template
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
    
    # Hisse kodlarını kısalt
    hisseler = clean_ticker_series(sharpe_like.index)
    degerler = sharpe_like.values
    
    fig = px.bar(
        x=hisseler,
        y=degerler,
        title=f"Riske Göre Düzeltilmiş Performans - {format_date(first_date)} ile {format_date(last_date)} arası",
        labels={'x': 'Hisseler', 'y': 'Getiri/Oynaklık Oranı'},
        color=degerler,
        color_continuous_scale=RETURN_COLOR_SCALE,
        text=[BAR_TEXT_FORMAT.format(val) for val in degerler]
    )
    
    fig.update_traces(
        textposition='outside',
        textfont=dict(size=TEXT_FONT_SIZE, color=HOVER_TEXT_COLOR),
        hovertemplate='<b>%{x}</b>: %{y:.4f}<extra></extra>'
    )
    
    # Y ekseni için 0 çizgisi ekle
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(hisseler)-0.5,
        y0=0,
        y1=0,
        line=dict(color="#aaaaaa", width=1, dash="dot")
    )
    
    return fig, info_text

@apply_figure_template
def plot_price_drawdown(stock_data, ticker):
    """Hisse fiyatı ve zirveden uzaklık grafiğini oluşturur"""
    
    # Veri hazırlama
    df = stock_data[[ticker]].copy()
    df.columns = ['Close']  # Sütun adını standartlaştır
    
    # Geri çekilme hesapla
    df['Peak'] = df['Close'].cummax()
    df['Drawdown'] = (df['Close'] - df['Peak']) / df['Peak'] * 100
    
    first_date = df.index[0]
    last_date = df.index[-1]
    clean_ticker_name = clean_ticker(ticker)
    
    # Geri çekilme ve fiyat için subplot oluştur
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=(
            f"{clean_ticker_name} Fiyat Grafiği",
            "Zirveden Uzaklık (%)"
        )
    )
    
    # Fiyat grafiği ekle
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Close'],
            name='Fiyat',
            line=dict(color=NEUTRAL_COLOR, width=LINE_WIDTH),
            hovertemplate='%{y:.2f}<br>%{x|%d.%m.%Y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Zirve fiyat
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Peak'],
            name='Zirve',
            line=dict(color='rgba(0,0,0,0.3)', width=1, dash='dot'),
            hovertemplate='%{y:.2f}<br>%{x|%d.%m.%Y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Geri çekilme grafiği
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Drawdown'],
            name='Zirveden Uzaklık (%)',
            fill='tozeroy',
            fillcolor='rgba(220, 53, 69, 0.2)',
            line=dict(color=DOWN_COLOR, width=1.5),
            hovertemplate='%{y:.2f}%<br>%{x|%d.%m.%Y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Grafik başlığı ve boyutu
    fig.update_layout(
        title=f"{clean_ticker_name} Zirveden Uzaklık Analizi - {format_date(first_date)} ile {format_date(last_date)} arası",
        height=GRAPH_HEIGHT
    )
    
    # En büyük düşüş miktarı
    max_drawdown = df['Drawdown'].min()
    max_drawdown_date = format_date(df.loc[df['Drawdown'].idxmin()].name)
    
    # Bilgi metni
    info_text = (
        f"ℹ️ **Zirveden Uzaklık Analizi:** Üstteki grafik hisse fiyatını ve şimdiye kadarki zirve noktaları gösterir. "
        f"Alttaki grafik, o anki fiyatın zirveden yüzde olarak ne kadar uzakta olduğunu gösterir. "
        f"<br><br>**{clean_ticker_name}** için bu periyotta en büyük düşüş: "
        f"**%{max_drawdown:.2f}** ({max_drawdown_date} tarihinde)"
    )
    
    return fig, info_text 