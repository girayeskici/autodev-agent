from langchain.tools import tool
from sandbox.docker_manager import DockerSandboxManager

sandbox_manager = DockerSandboxManager()

@tool
def terminal_komutu_calistir(komut: str) -> str:
    """
    Kodu izole Docker Linux sandbox içinde derler ve çalıştırır.
    Örnek komutlar:
    - 'python3 test_hesap.py'
    - 'gcc main.c -o main && ./main'
    - 'pytest'
    """
    sonuc = sandbox_manager.execute_command(komut)
    cikti = []
    
    cikti.append(f"Durum Kodu: {sonuc['exit_code']}")
    if sonuc["stdout"]:
        cikti.append(f"[STANDART ÇIKTI]:\n{sonuc['stdout']}")
    if sonuc["stderr"]:
        cikti.append(f"[HATA ÇIKTISI]:\n{sonuc['stderr']}")
        
    return "\n".join(cikti)