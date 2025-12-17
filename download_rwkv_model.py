"""
Script para baixar o modelo RWKV-5 3B do HuggingFace
"""
from huggingface_hub import hf_hub_download
import os

# Criar diretório para modelos se não existir
models_dir = "models"
os.makedirs(models_dir, exist_ok=True)

# Baixar modelo RWKV-5 3B (World version)
print("Baixando modelo RWKV-5 World 3B...")
print("Isso pode levar alguns minutos dependendo da sua conexão...")

try:
    model_path = hf_hub_download(
        repo_id="BlinkDL/rwkv-5-world",
        filename="RWKV-5-World-3B-v2-20231113-ctx4096.pth",
        local_dir=models_dir,
        local_dir_use_symlinks=False
    )
    
    print(f"\n✅ Modelo baixado com sucesso!")
    print(f"📁 Local: {model_path}")
    print(f"\nPara usar o modelo:")
    print(f"  from rwkv.model import RWKV")
    print(f"  model = RWKV(model='{model_path}', strategy='cpu fp32')")
    
except Exception as e:
    print(f"❌ Erro ao baixar modelo: {e}")
    print("\nAlternativa: Baixe manualmente de:")
    print("https://huggingface.co/BlinkDL/rwkv-5-world/tree/main")
