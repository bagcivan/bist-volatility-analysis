import streamlit as st
import datetime
from formatters import (
    format_datetime
)
# HTML Bileşenleri
class HtmlComponent:
    """HTML bileşenleri oluşturmak için temel sınıf"""
    
    @staticmethod
    def create_html(html_content):
        """HTML içeriğini Streamlit'e güvenle yerleştirmek için yardımcı metod"""
        return st.markdown(html_content, unsafe_allow_html=True)

    @staticmethod
    def render_to_streamlit(html_content):
        """HTML içeriğini doğrudan Streamlit'e yerleştir"""
        st.markdown(html_content, unsafe_allow_html=True)

class StyledDataFrame(HtmlComponent):
    """Biçimlendirilmiş veri çerçevesi bileşeni"""
    
    @staticmethod
    def create(data, title, title_class, formatter_func=None):
        """Başlık ve biçimlendirilmiş içeriğe sahip bir veri çerçevesi oluşturur"""
        # Başlık HTML'i
        title_html = f'<p class="list-title list-title-{title_class}">{title}</p>'
        
        # DataFrame stil
        styled_df = data.style
        
        # Biçimlendirici fonksiyon varsa uygula
        if formatter_func and 'Getiri (%)' in data.columns:
            styled_df = styled_df.format({'Getiri (%)': formatter_func})
        
        # Stil ayarlarını uygula ve indeksi gizle
        styled_df = styled_df.hide(axis="index")
        
        # HTML olarak döndür
        df_html = styled_df.to_html()
        
        return title_html, df_html

class LastUpdateInfo(HtmlComponent):
    """Son güncelleme bilgisi bileşeni"""
    
    @staticmethod
    def create(last_date, current_time=None):
        """Son güncelleme bilgisini formatlayan fonksiyon"""
        if current_time is None:
            current_time = datetime.datetime.now()
            
        update_time = format_datetime(current_time.replace(year=last_date.year, month=last_date.month, day=last_date.day))
        return f'<div class="last-update">Son güncelleme: {update_time}</div>'
