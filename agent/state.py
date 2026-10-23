from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    AutoDev-Agent çalışma döngüsü boyunca tutulan durum yapısı.
    """
    # add_messages: Yeni mesaj geldikçe listeyi ezmek yerine ucuna ekler (append)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Ajanın kaçıncı denemede olduğunu izlemek için sayaç (sonsuz döngüyü engeller)
    iteration_count: int
    
    # Kullanıcının verdiği orijinal görev
    task: str