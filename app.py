import os
import streamlit as st
from langchain_core.messages import HumanMessage
from agent.graph import app

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "workspace"))

st.set_page_config(
    page_title="AutoDev-Agent Dashboard",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AutoDev-Agent: Otonom Kod Onarım Paneli")
st.caption("LangGraph, Docker Sandbox ve Gemini tabanlı izole hata tespit ve onarım sistemi")

sol_kolon, sag_kolon = st.columns([1.2, 0.8])

def dosyalari_tara():
    dosyalar = []
    if os.path.exists(BASE_DIR):
        for kok, _, files in os.walk(BASE_DIR):
            if ".git" in kok:
                continue
            for f in files:
                if f != ".gitkeep":
                    rel = os.path.relpath(os.path.join(kok, f), BASE_DIR)
                    dosyalar.append(rel)
    return dosyalar

with sag_kolon:
    st.subheader("📁 Workspace Dosya İzleyici")
    mevcut_dosyalar = dosyalari_tara()
    if mevcut_dosyalar:
        secilen_dosya = st.selectbox("İncelemek istediğiniz dosya:", mevcut_dosyalar)
        dosya_yolu = os.path.join(BASE_DIR, secilen_dosya)
        with open(dosya_yolu, "r", encoding="utf-8", errors="ignore") as f:
            st.code(f.read(), language="python" if secilen_dosya.endswith(".py") else "text")
    else:
        st.info("Workspace dizini henüz boş.")

with sol_kolon:
    st.subheader("📋 Görev Tanımı")
    varsayilan_gorev = (
        "workspace içindeki dosyaları incele, testleri Docker sandbox içinde pytest ile çalıştır. "
        "Hataları analiz et, hesapla.py dosyasındaki hatayı düzeltip testlerin hepsinin geçmesini sağla "
        "ve son olarak değişiklikleri git ile commit'le."
    )
    gorev_metni = st.text_area("Ajan için Görev:", value=varsayilan_gorev, height=90)
    baslat_butonu = st.button("🚀 Ajanı Çalıştır", type="primary", use_container_width=True)

    if baslat_butonu and gorev_metni:
        st.divider()
        st.subheader("⚙️ Canlı İşlem Günlüğü")
        
        baslangic_durumu = {
            "messages": [HumanMessage(content=gorev_metni)],
            "iteration_count": 0,
            "task": gorev_metni
        }
        
        islem_alani = st.container()
        
        try:
            with st.spinner("Ajan düşünüyor ve araçları tetikliyor..."):
                for event in app.stream(baslangic_durumu, stream_mode="values"):
                    mesajlar = event.get("messages", [])
                    if not mesajlar:
                        continue
                    
                    son_mesaj = mesajlar[-1]
                    
                    # Araç Çağrısı
                    if hasattr(son_mesaj, "tool_calls") and son_mesaj.tool_calls:
                        for tc in son_mesaj.tool_calls:
                            with islem_alani:
                                st.info(f"🛠️ **Araç Çağrıldı:** `{tc['name']}`")
                                st.caption(f"Parametreler: {tc['args']}")
                    
                    # Araç Yanıtı
                    elif son_mesaj.type == "tool":
                        with islem_alani:
                            with st.expander(f"📥 Araç Çıktısı: {son_mesaj.name}", expanded=False):
                                st.code(str(son_mesaj.content))
                    
                    # Ajan Yanıtı
                    elif son_mesaj.type == "ai" and not getattr(son_mesaj, "tool_calls", None):
                        with islem_alani:
                            st.success("🎯 **Ajan Çözümü Tamamladı:**")
                            st.markdown(son_mesaj.content)

            st.balloons()
            st.rerun()

        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")