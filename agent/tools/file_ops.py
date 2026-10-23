import os
from langchain.tools import tool

# Workspace dizinini mutlak yol olarak al
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "workspace"))

def _guvenli_yol(dosya_yolu: str) -> str:
    """Workspace dışına çıkılmasını (Path Traversal açığını) engelleyen güvenlik kontrolü."""
    hedef_yol = os.path.abspath(os.path.join(BASE_DIR, dosya_yolu))
    if not hedef_yol.startswith(BASE_DIR):
        raise ValueError("Güvenlik İhlali: Workspace dizini dışındaki dosyalara erişilemez!")
    return hedef_yol

@tool
def dosya_oku(dosya_yolu: str) -> str:
    """Belirtilen göreceli yoldaki dosyanın içeriğini okur."""
    try:
        tam_yol = _guvenli_yol(dosya_yolu)
        if not os.path.exists(tam_yol):
            return f"Hata: '{dosya_yolu}' dosyası bulunamadı."
        with open(tam_yol, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Dosya okuma hatası: {str(e)}"

@tool
def dosya_yaz(dosya_yolu: str, icerik: str) -> str:
    """Belirtilen yola dosya yazar veya mevcut dosyanın içeriğini günceller."""
    try:
        tam_yol = _guvenli_yol(dosya_yolu)
        os.makedirs(os.path.dirname(tam_yol), exist_ok=True)
        with open(tam_yol, "w", encoding="utf-8") as f:
            f.write(icerik)
        return f"Başarılı: '{dosya_yolu}' dosyası kaydedildi."
    except Exception as e:
        return f"Dosya yazma hatası: {str(e)}"

@tool
def dizin_listele(alt_dizin: str = "") -> str:
    """Workspace içindeki mevcut dosya ve klasörleri listeler."""
    try:
        hedef = _guvenli_yol(alt_dizin) if alt_dizin else BASE_DIR
        if not os.path.exists(hedef):
            return f"Hata: Dizin bulunamadı: {alt_dizin}"
        
        elemanlar = []
        for root, dirs, files in os.walk(hedef):
            rel_path = os.path.relpath(root, BASE_DIR)
            prefix = "" if rel_path == "." else f"{rel_path}/"
            for d in dirs:
                elemanlar.append(f"[KLASÖR] {prefix}{d}")
            for f in files:
                if f != ".gitkeep":
                    elemanlar.append(f"[DOSYA]  {prefix}{f}")
        return "\n".join(elemanlar) if elemanlar else "Dizin boş."
    except Exception as e:
        return f"Dizin listeleme hatası: {str(e)}"