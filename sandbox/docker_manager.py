import os
import docker
from typing import Dict, Any, Optional

class DockerSandboxManager:
    """
    Ajanın ürettiği kodları güvenli, izole bir Docker konteynerinde 
    çalıştıran ve sonuçları toplayan yönetici sınıf.
    """
    def __init__(self, image_name: str = "autodev-sandbox:latest", workspace_dir: Optional[str] = None):
        self.image_name = image_name
        self.client = docker.from_env()
        
        # Ana makinedeki workspace dizininin mutlak yolu
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.workspace_dir = workspace_dir or os.path.join(base_dir, "workspace")
        
        # workspace klasörü yoksa oluştur
        os.makedirs(self.workspace_dir, exist_ok=True)

    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Konteyner içinde belirtilen kabuk komutunu çalıştırır.
        Ana makinedeki workspace dizini konteyner içindeki /workspace ile senkronizedir.
        """
        container = None
        try:
            # Geçici bir izole konteyner başlat
            container = self.client.containers.create(
                image=self.image_name,
                command="/bin/bash",
                stdin_open=True,
                tty=True,
                volumes={
                    self.workspace_dir: {
                        "bind": "/workspace",
                        "mode": "rw"
                    }
                },
                working_dir="/workspace",
                network_disabled=True # Güvenlik: Ajanın dış ağa kontrolsüz erişimini kısıtlar
            )
            
            container.start()

            # Komutu konteyner içinde yürüt
            exec_result = container.exec_run(
                cmd=["/bin/bash", "-c", command],
                workdir="/workspace",
                demux=True # stdout ve stderr çıktılarını ayrı yakalar
            )

            exit_code = exec_result.exit_code
            stdout_bytes, stderr_bytes = exec_result.output

            stdout = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
            stderr = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""

            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "stdout": stdout.strip(),
                "stderr": stderr.strip()
            }

        except docker.errors.ImageNotFound:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Hata: '{self.image_name}' Docker imajı bulunamadı. Lütfen önce derleyin."
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Konteyner çalıştırma hatası: {str(e)}"
            }
        finally:
            if container:
                try:
                    container.stop(timeout=1)
                    container.remove(force=True)
                except Exception:
                    pass