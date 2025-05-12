# BIST Hisseleri Oynaklık Analizi

Bu Streamlit uygulaması, BIST hisselerinin oynaklık ve performans analizini görselleştirmek için kullanılır.

## Özellikler

- BIST-30 hisselerinin veri indirme
- Özel hisse kodu listesi kullanabilme
- Oynaklık (varyasyon katsayısı) hesaplama ve analiz
- Çeşitli görselleştirmeler:
  - En oynak hisseler grafiği
  - Oynaklık ısı haritası
  - Son gün oynaklık bar grafiği
  - Momentum analizi
  - Oynaklık vs getiri scatter plot
  - Risk-getiri performans analizi

## Kurulum

1. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:

```bash
streamlit run app.py
```

## Kullanım

- Sol kenar çubuğundaki parametreleri değiştirerek analiz ayarlarını değiştirebilirsiniz
- "Verileri Yenile" butonuna basarak güncel fiyat verilerini alabilirsiniz
- "Gösterge Seçimi" kısmından istediğiniz analiz görselini seçebilirsiniz

## Gereksinimler

- Python 3.7+
- Streamlit
- Pandas
- Plotly
- Matplotlib
- Seaborn
- curl-cffi 