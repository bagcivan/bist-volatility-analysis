import functools

# Önbelleğe alma dekoratörü
def memoize(func):
    """Fonksiyon sonuçlarını önbelleğe alır
    
    Fonksiyon sonuçlarını tekrar hesaplamamak için bir önbellek mekanizması sağlar.
    Aynı parametrelerle tekrar çağrıldığında, hesaplama yapmak yerine önbellekteki sonucu döndürür.
    
    Args:
        func: Önbelleğe alınacak fonksiyon
        
    Returns:
        Önbelleğe alınmış fonksiyon
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Her parametre dönüştürülebilir olmalı
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper

def extract_page_title(page_name):
    """Sayfa adından emoji'yi kaldırarak başlığı çıkarır
    
    Args:
        page_name: Emoji içerebilen sayfa adı (örn. "📊 Piyasa Özeti")
        
    Returns:
        Emoji'siz sayfa başlığı (örn. "Piyasa Özeti")
    """
    return page_name.split(" ", 1)[1] if " " in page_name else page_name

