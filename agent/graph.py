import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.tools import tum_araclar

# .env ortam değişkenlerini yükle
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

# Model adını doğrudan sabit olarak veriyoruz
llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
# Araçları modele bağla
llm_with_tools = llm.bind_tools(tum_araclar)

SISTEM_MESAJI = """Sen kıdemli bir otonom yazılım mühendisi ve hata onarım ajanısın (AutoDev-Agent).
Sana verilen görevleri 'workspace' dizini içinde izole bir şekilde çözersin.

İş akışın şu adımları takip etmelidir:
1. Dizin içeriğini incele (`dizin_listele`) ve ilgili dosyaları oku (`dosya_oku`).
2. Çalışmaya başlamadan önce yeni bir git branch'i aç (`git_branch_olustur`).
3. Mevcut testleri veya kodu Docker sandbox içinde çalıştırarak hatayı netleştir (`terminal_komutu_calistir`).
4. Hatayı analiz et ve dosyayı düzelt (`dosya_yaz`).
5. Kodu tekrar sandbox içinde test et. Hata devam ediyorsa tekrar düzelt.
6. Tüm testler geçtiğinde yapılan değişiklikleri commit'le (`git_commit_at`).
7. Kullanıcıya ne yaptığını, hangi hatayı çözdüğünü ve sonucu net şekilde özetle.

Not: Kendi kafandan test uydurma, mutlaka sandbox aracını kullanarak gerçek derleme/çalıştırma çıktısını gör.
"""

def agent_dugumu(state: AgentState):
    mesajlar = state["messages"]
    if not any(m.type == "system" for m in mesajlar):
        from langchain_core.messages import SystemMessage
        mesajlar = [SystemMessage(content=SISTEM_MESAJI)] + list(mesajlar)
    
    yanit = llm_with_tools.invoke(mesajlar)
    yeni_sayac = state.get("iteration_count", 0) + 1
    
    return {
        "messages": [yanit],
        "iteration_count": yeni_sayac
    }

arac_dugumu = ToolNode(tum_araclar)

def nereye_gidecek(state: AgentState):
    son_mesaj = state["messages"][-1]
    if state.get("iteration_count", 0) >= 15:
        return END
    if hasattr(son_mesaj, "tool_calls") and len(son_mesaj.tool_calls) > 0:
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_dugumu)
workflow.add_node("tools", arac_dugumu)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    nereye_gidecek,
    {"tools": "tools", END: END}
)
workflow.add_edge("tools", "agent")

app = workflow.compile()