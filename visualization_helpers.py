import pandas as pd
import plotly.express as px
from constants import (
    PLOT_BGCOLOR, PAPER_BGCOLOR, GRID_COLOR
)
from formatters import format_date, clean_ticker_series

def set_figure_template(fig):
    """Grafiklere tutarlı tema uygular"""
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=12, color="#333333"),
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PAPER_BGCOLOR,
        margin=dict(t=50, l=40, r=30, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='#E5E5E5',
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=11,
            font_family="Arial, sans-serif"
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            zeroline=False,
            tickfont=dict(size=10),
            title_font=dict(size=11)
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            zeroline=False,
            tickfont=dict(size=10),
            title_font=dict(size=11)
        )
    )
    return fig

def apply_figure_template(func):
    """
    Grafik fonksiyonları için dekoratör.
    Fonksiyonun döndürdüğü grafiğe otomatik olarak tema ayarlarını uygular.
    
    Kullanım:
    @apply_figure_template
    def herhangi_bir_grafik_fonksiyonu(parametreler):
        # Grafik çizimi
        fig = ...
        info_text = ...
        return fig, info_text
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, tuple) and len(result) >= 1:
            fig = result[0]
            # Tema ayarlarını uygula
            fig = set_figure_template(fig)
            # Aynı tuple'ı döndür ama fig güncellenmiş olsun
            return (fig,) + result[1:]
        return result
    return wrapper

class PlotHelpers:
    """Görselleştirme işlemlerinde tekrar eden ortak fonksiyonları sağlar"""
    
    @staticmethod
    def create_bar_chart(x_data, y_data, title, x_label='Hisseler', y_label='Değer', 
                         color_scale=None, text_format=None, precision=2):
        """Bar grafiği oluşturmak için ortak fonksiyon
        
        Args:
            x_data: x ekseni verileri (genellikle hisse kodları)
            y_data: y ekseni verileri (genellikle değerler)
            title: Grafik başlığı
            x_label: x ekseni etiketi
            y_label: y ekseni etiketi 
            color_scale: Kullanılacak renk skalası
            text_format: Metin formatı şablonu veya None
            precision: Ondalık hassasiyet
            
        Returns:
            Plotly figürü
        """
        from constants import (
            RETURN_COLOR_SCALE, TEXT_FONT_SIZE, HOVER_TEXT_COLOR
        )
        
        # Varsayılan değerleri ayarla
        color_scale = color_scale or RETURN_COLOR_SCALE
        
        # Metin formatlaması
        if text_format:
            text_values = [text_format.format(val) for val in y_data]
        else:
            format_str = f"{{:.{precision}f}}"
            text_values = [format_str.format(val) for val in y_data]
            
        # Bar grafiği oluştur
        fig = px.bar(
            x=x_data,
            y=y_data,
            title=title,
            labels={'x': x_label, 'y': y_label},
            color=y_data,
            color_continuous_scale=color_scale,
            text=text_values
        )
        
        # Standart özellikler
        fig.update_traces(
            textposition='outside',
            textfont=dict(size=TEXT_FONT_SIZE, color=HOVER_TEXT_COLOR),
            hovertemplate=f'<b>%{{x}}</b>: %{{y:.{precision}f}}<extra></extra>'
        )
        
        return fig
    
    @staticmethod
    def add_zero_line(fig, x_data):
        """Grafiklere yatay sıfır çizgisi ekleme
        
        Args:
            fig: Plotly figürü
            x_data: x ekseni verisi
            
        Returns:
            Güncellenmiş figür
        """
        fig.add_shape(
            type="line",
            x0=-0.5,
            x1=len(x_data)-0.5,
            y0=0,
            y1=0,
            line=dict(color="#aaaaaa", width=1, dash="dot")
        )
        return fig
    
    @staticmethod
    def get_date_range_title(first_date, last_date, base_title):
        """Tarih aralığı içeren başlık metni oluşturur
        
        Args:
            first_date: Başlangıç tarihi
            last_date: Bitiş tarihi
            base_title: Temel başlık metni
            
        Returns:
            Tarih aralığı eklenmiş başlık
        """
        return f"{base_title} - {format_date(first_date)} ile {format_date(last_date)} arası"
    
    @staticmethod
    def prepare_stock_data(data, clean_names=True, sort_by=None, ascending=False, top_n=None):
        """Hisse verilerini görselleştirme için hazırlar
        
        Args:
            data: Seri veya DataFrame olarak hisse verileri
            clean_names: Hisse isimlerinden '.IS' ekini temizle
            sort_by: Sıralama kriteri ('value' veya index'in bir kolonu)
            ascending: Sıralama yönü (True=artan, False=azalan)
            top_n: En üst N veriyi seç
        
        Returns:
            Tuple: (temizlenmiş hisse kodları, değerler)
        """
        # Eğer DataFrame ise önce seri haline getir
        if isinstance(data, pd.DataFrame):
            if sort_by == 'value':
                data = data.iloc[-1].sort_values(ascending=ascending)
            elif sort_by is not None:
                data = data.sort_values(by=sort_by, ascending=ascending).iloc[-1]
            else:
                data = data.iloc[-1]
        else:  # Seri ise direkt devam et
            if sort_by == 'value':
                data = data.sort_values(ascending=ascending)
        
        # En üst N veriyi al
        if top_n is not None:
            data = data.iloc[:top_n]
        
        # Hisse kodlarını temizle
        if clean_names:
            hisseler = clean_ticker_series(data.index)
        else:
            hisseler = data.index
        
        # Değerleri döndür
        degerler = data.values
        
        return hisseler, degerler
        
    @staticmethod
    def create_line_chart(df, title, y_label='Değer', x_label='Tarih', color_sequence=None, 
                          line_width=None, hover_precision=4):
        """Zaman serisi çizgi grafiği oluşturur
        
        Args:
            df: Çizilecek DataFrame
            title: Grafik başlığı
            y_label: Y ekseni etiketi
            x_label: X ekseni etiketi
            color_sequence: Renk serisi
            line_width: Çizgi kalınlığı
            hover_precision: Hover değer hassasiyeti
            
        Returns:
            Plotly figürü
        """
        from constants import (
            COLOR_SCALE, LINE_WIDTH
        )
        
        # Varsayılan değerleri ayarla
        color_sequence = color_sequence or COLOR_SCALE
        line_width = line_width or LINE_WIDTH
        
        # Çizgi grafiği oluştur
        fig = px.line(
            df,
            x=df.index,
            y=df.columns,
            title=title,
            color_discrete_sequence=color_sequence,
            labels={"value": y_label, "variable": "Hisse", "x": x_label}
        )
        
        # Standart özellikler
        fig.update_traces(
            line=dict(width=line_width),
            hovertemplate=f'<b>%{{y:.{hover_precision}f}}</b><br>%{{x|%d.%m.%Y}}<extra>%{{fullData.name}}</extra>'
        )
        
        return fig 