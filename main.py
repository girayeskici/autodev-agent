import sys
from langchain_core.messages import HumanMessage
from agent.graph import app

def ajani_calistir(gorev: str):
    """
    Kullanıcının verdiği görevi LangGraph ajanına teslim eder
    ve yürütme döngüsünü konsolda adım adım görselleştirir.
    """
    print("\n" + "=" * 60)
    print(f"🚀 GÖREV BAŞLATILDI: {gorev}")
    print("=" * 60 + "\n")

    baslangic_durumu = {
        "messages": [HumanMessage(content=gorev)],
        "iteration_count": 0,
        "task": gorev
    }

    # Graph üzerinden adımları canlı akış (stream) olarak alıyoruz
    for event in app.stream(baslangic_durumu, stream_mode="values"):
        mesajlar = event.get("messages", [])
        if not mesajlar:
            continue
        
        son_mesaj = mesajlar[-1]
        
        # Ajan bir araca başvurmak istediğinde (Tool Call)
        if hasattr(son_mesaj, "tool_calls") and son_mesaj.tool_calls:
            for tc in son_mesaj.tool_calls:
                print(f"🛠️  [ARAÇ ÇAĞRISI] -> {tc['name']}")
                print(f"    Parametreler: {tc['args']}\n")
        
        # Aracın döndürdüğü yanıt (Tool Output)
        elif son_mesaj.type == "tool":
            print(f"📥 [ARAÇ ÇIKTISI] -> {son_mesaj.name}")
            icerik = str(son_mesaj.content).strip()
            # Çıktı çok uzunsa ekranda sade göstermek için kısaltalım
            if len(icerik) > 300:
                print(f"    {icerik[:300]}... [kısaltıldı]\n")
            else:
                print(f"    {icerik}\n")

        # Ajan nihai kararını verip kullanıcıya özet sunduğunda
        elif son_mesaj.type == "ai" and not getattr(son_mesaj, "tool_calls", None):
            print("\n" + "-" * 60)
            print("🤖 [AJAN YANITI]:")
            print(son_mesaj.content)
            print("-" * 60 + "\n")

def main():
    print("""
    ==================================================
           🤖 AutoDev-Agent: Otonom Kod Onarıcı
    ==================================================
    Çıkmak için 'q' veya 'exit' yazabilirsiniz.
    """)
    
    while True:
        try:
            kullanici_girdisi = input("\n👉 Ajan için bir görev girin: ").strip()
            if not kullanici_girdisi:
                continue
            if kullanici_girdisi.lower() in ["q", "exit", "cikis"]:
                print("Ajan oturumu sonlandırıldı.")
                sys.exit(0)
            
            ajani_calistir(kullanici_girdisi)
            
        except KeyboardInterrupt:
            print("\nİşlem iptal edildi.")
            break
        except Exception as e:
            print(f"\n❌ Bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    main()