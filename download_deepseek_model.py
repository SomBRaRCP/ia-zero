#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_deepseek_model.py

Baixa o DeepSeek-Coder-V2-Lite-Instruct (16B) para uso local.
Modelo otimizado para extração estrutural de código e conhecimento.

Modelo: deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct
Tamanho: ~16GB (BF16) ou ~9GB (INT8 quantizado)
"""

import os
from pathlib import Path

def check_model_exists():
    """Verifica se o modelo já foi baixado."""
    model_dir = Path("./models/deepseek-coder-v2-lite")
    
    if not model_dir.exists():
        return False
    
    # Verifica se tem arquivos essenciais
    has_config = (model_dir / "config.json").exists()
    has_weights = len(list(model_dir.glob("*.safetensors"))) > 0
    
    return has_config and has_weights

def download_deepseek_local():
    """
    Baixa o modelo DeepSeek-Coder-V2-Lite-Instruct do HuggingFace.
    
    Especificações:
    - Modelo: deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct
    - Tamanho: ~16GB (BF16 completo)
    - RAM necessária: ~24GB
    - VRAM ideal: 16GB+ (GPU) ou roda em CPU (mais lento)
    """
    try:
        from huggingface_hub import snapshot_download
        print("✅ huggingface_hub encontrado")
    except ImportError:
        print("❌ Biblioteca 'huggingface_hub' não encontrada")
        print("   Instale com: pip install huggingface_hub")
        return None
    
    model_id = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
    local_dir = Path("./models/deepseek-coder-v2-lite")
    local_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("DOWNLOAD: DeepSeek-Coder-V2-Lite-Instruct")
    print("=" * 60)
    print(f"\nModelo: {model_id}")
    print(f"Destino: {local_dir.absolute()}")
    print(f"Tamanho estimado: ~16GB")
    print("\nEste download pode demorar de 10 a 60 minutos dependendo da conexão.")
    print("O download pode ser pausado e retomado.\n")
    
    confirm = input("Deseja continuar? (s/n): ")
    if confirm.lower() != 's':
        print("\n❌ Download cancelado")
        return None
    
    try:
        print("\n🔄 Iniciando download...\n")
        
        downloaded_path = snapshot_download(
            repo_id=model_id,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False,
            resume_download=True,
            # Baixa apenas arquivos essenciais (não exemplos/docs)
            allow_patterns=[
                "*.json",
                "*.safetensors",
                "*.model",
                "*.tiktoken",
                "tokenizer.model"
            ],
            ignore_patterns=[
                "*.md",
                "*.txt",
                "*.py",
                ".git*"
            ]
        )
        
        print("\n" + "=" * 60)
        print("✅ DOWNLOAD COMPLETO!")
        print("=" * 60)
        print(f"\n📁 Modelo salvo em: {local_dir.absolute()}")
        print("\n🧪 Para testar:")
        print("   python test_deepseek_integration.py")
        
        return str(local_dir)
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Download pausado.")
        print("   Execute novamente para retomar de onde parou.")
        return None
    except Exception as e:
        print(f"\n❌ Erro durante download: {e}")
        print("\nDicas:")
        print("1. Verifique sua conexão com internet")
        print("2. Certifique-se de ter ~20GB de espaço livre")
        print("3. Execute novamente para retomar o download")
        return None

def test_model_loading():
    """Testa se o modelo pode ser carregado."""
    model_dir = Path("./models/deepseek-coder-v2-lite")
    
    if not check_model_exists():
        print("❌ Modelo não encontrado. Execute o download primeiro.")
        return False
    
    print("\n" + "=" * 60)
    print("TESTE: Carregando Modelo")
    print("=" * 60)
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        print("\n🔄 Carregando tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            str(model_dir),
            trust_remote_code=True
        )
        print("✅ Tokenizer carregado")
        
        print("\n🔄 Carregando modelo (pode demorar alguns minutos)...")
        
        # Detecta se tem GPU disponível
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Dispositivo: {device}")
        
        if device == "cpu":
            print("   ⚠️  Usando CPU (será mais lento)")
            print("   💡 Para GPU: instale torch com CUDA")
        
        model = AutoModelForCausalLM.from_pretrained(
            str(model_dir),
            trust_remote_code=True,
            torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None
        )
        
        print("✅ Modelo carregado com sucesso!")
        
        # Teste simples
        print("\n🧪 Teste de inferência...")
        messages = [{"role": "user", "content": "Olá"}]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)
        
        outputs = model.generate(
            inputs,
            max_new_tokens=20,
            do_sample=False
        )
        
        response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
        print(f"   Resposta: {response}")
        
        print("\n✅ Modelo funcionando corretamente!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Biblioteca faltando: {e}")
        print("\nInstale as dependências:")
        print("   pip install transformers torch accelerate")
        return False
    except Exception as e:
        print(f"\n❌ Erro ao carregar modelo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DEEPSEEK-CODER-V2-LITE - SETUP LOCAL")
    print("=" * 60)
    
    # Verifica se já existe
    if check_model_exists():
        print("\n✅ Modelo já baixado!")
        print(f"   Localização: {Path('./models/deepseek-coder-v2-lite').absolute()}")
        
        test = input("\nDeseja testar o carregamento? (s/n): ")
        if test.lower() == 's':
            test_model_loading()
    else:
        print("\n📥 Modelo não encontrado localmente")
        print("\nRequisitos:")
        print("  • ~20GB de espaço em disco")
        print("  • ~24GB RAM (ou 16GB VRAM se usar GPU)")
        print("  • Conexão estável de internet")
        
        download_deepseek_local()
