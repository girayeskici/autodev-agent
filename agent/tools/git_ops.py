import os
import git
from langchain.tools import tool

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "workspace"))

def _repo_al() -> git.Repo:
    """Workspace içindeki Git reposunu döner, yoksa oluşturur."""
    try:
        return git.Repo(BASE_DIR)
    except git.exc.InvalidGitRepositoryError:
        return git.Repo.init(BASE_DIR)

@tool
def git_branch_olustur(branch_adi: str) -> str:
    """Yeni bir Git çalışma dalı (branch) oluşturur ve ona geçer."""
    try:
        repo = _repo_al()
        yeni_dal = repo.create_head(branch_adi)
        yeni_dal.checkout()
        return f"Başarılı: '{branch_adi}' dalı oluşturuldu ve geçiş yapıldı."
    except Exception as e:
        return f"Branch oluşturma hatası: {str(e)}"

@tool
def git_commit_at(mesaj: str) -> str:
    """Yapılan tüm dosya değişikliklerini Git üzerinde commit eder."""
    try:
        repo = _repo_al()
        repo.git.add(A=True)
        commit = repo.index.commit(mesaj)
        return f"Başarılı: '{mesaj}' mesajı ile commit atıldı (Hash: {commit.hexsha[:7]})."
    except Exception as e:
        return f"Commit hatası: {str(e)}"