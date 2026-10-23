from agent.tools.file_ops import dosya_oku, dosya_yaz, dizin_listele
from agent.tools.sandbox_ops import terminal_komutu_calistir
from agent.tools.git_ops import git_branch_olustur, git_commit_at

tum_araclar = [
    dosya_oku,
    dosya_yaz,
    dizin_listele,
    terminal_komutu_calistir,
    git_branch_olustur,
    git_commit_at
]