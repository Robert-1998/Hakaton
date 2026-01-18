# download_force.py
from huggingface_hub import snapshot_download
import os

print("--- НАЧАЛО ПРИНУДИТЕЛЬНОГО СКАЧИВАНИЯ (ОДИН ПОТОК) ---")

local_dir = "./my_local_model"

try:
    path = snapshot_download(
        repo_id="ai-forever/rugpt3small_based_on_gpt2",
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        resume_download=True,
        max_workers=1                  # <--- ИЗМЕНЕНО: ОДИН ПОТОК!
    )
    print(f"\n✅ УСПЕХ! Модель скачана в папку: {local_dir}")
except Exception as e:
    print(f"\n❌ Ошибка скачивания: {e}")
    print("Попробуйте запустить этот скрипт еще раз, он продолжит скачивание.")