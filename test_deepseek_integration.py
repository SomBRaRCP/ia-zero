#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_deepseek_integration.py

Teste de integração com DeepSeek-Coder-V2-Lite (modelo local)
"""

import os
from pathlib import Path
from core.knowledge_miner import KnowledgeMiner

def test_model_exists():
    """Testa se o modelo foi baixado"""
    print("=" * 60)
    print("TESTE 1: Modelo Local")
    print("=" * 60)
    
    model_path = Path("./models/deepseek-coder-v2-lite")
    
    if not model_path.exists():
        print("❌ Modelo não encontrado")
        print(f"   Procurado em: {model_path.absolute()}")
        print("\nPara baixar:")
        print("   python download_deepseek_model.py")
        return False
    
    # Verifica arquivos essenciais
    has_config = (model_path / "config.json").exists()
    has_weights = len(list(model_path.glob("*.safetensors"))) > 0
    
    if has_config and has_weights:
        print(f"✅ Modelo encontrado em: {model_path.absolute()}")
        print(f"   Config: {'✅' if has_config else '❌'}")
        print(f"   Weights: {len(list(model_path.glob('*.safetensors')))} arquivos")
        return True
    else:
        print("⚠️  Modelo incompleto")
        print(f"   Config: {'✅' if has_config else '❌'}")
        print(f"   Weights: {'✅' if has_weights else '❌'}")
        return False

def test_miner_initialization():
    """Testa inicialização do minerador"""
    print("\n" + "=" * 60)
    print("TESTE 2: Inicialização do Minerador")
    print("=" * 60)
    
    try:
        miner = KnowledgeMiner()
        print("✅ KnowledgeMiner inicializado")
        
        if miner.model_path.exists():
            print(f"✅ Caminho do modelo configurado: {miner.model_path}")
            return True
        else:
            print("⚠️  Modelo não encontrado (modo mock)")
            return False
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return False

def test_dependencies():
    """Testa se as bibliotecas necessárimodelo)"""
    print("\n" + "=" * 60)
    print("TESTE 4: Extração Mock")
    print("=" * 60)
    
    try:
        miner = KnowledgeMiner()
        # Força modo mock
        miner.model = None
        
        candidatos = miner.extract_candidates("energia", "fisica")
        
        print(f"\n📊 Resultados:")
        print(f"   Total: {len(candidatos)} candidatos")
        
        for c in candidatos:
            print(f"   • {c.de} --[{c.tipo}]--> {c.para}")
            print(f"     Confiança: {c.confianca:.2f}")
        
        print("\n✅ Extração mock funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro na extração mock: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_extraction_local():
    """Testa extração com modelo local (se disponível)"""
    print("\n" + "=" * 60)
    print("TESTE 5: Extração com Modelo Local")
    print("=" * 60)
    
    model_path = Path("./models/deepseek-coder-v2-lite")
    
    if not model_path.exists():
        print("⏭️  Pulando (modelo não baixado)")
        print("   Para baixar: python download_deepseek_model.py")
        return None
    
    try:
        print("🔬 Inicializando minerador...")
        miner = KnowledgeMiner()
        
        print("🔬 Extraindo relações para 'energia' (campo: fisica)...")
        print("   (Primeira extração pode demorar 1-3 min para carregar modelo)")
        
        candidatos = miner.extract_candidates(
            conceito_raiz="energia",
            contexto="fisica",
            max_relacoes=3
        )
        
        print(f"\n📊 Resultados do Modelo Local:")
        print(f"   Total: {len(candidatos)} candidatos")
        
        for i, c in enumerate(candidatos, 1):
            print(f"\n   [{i}] {c.de} --[{c.tipo}]--> {c.para}")
            print(f"       Confiança: {c.confianca:.2f}")
            if c.evidencia:
                print(f"       Evidência: {c.evidencia[:60]}...")
        
        print("\n✅ Extração com modelo local funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na extração: {e}")
        import traceback
        traceback.print_exc()
        return Falseexidef minerar_conhecimento_profundo(conceitos: list[str], verbose: bool = True):
    """
    Usa DeepSeek para minerar relações profundas.
    IMPORTANTE: Candidatos vão para QUARENTENA (validação manual).
    """
    
    print("\n" + "=" * 70)
    print("FASE 3: MINERAÇÃO COM DEEPSEEK (→ quarentena)")
    print("=" * 70 + "\n")
    
    miner = KnowledgeMiner()
    
    for conceito in conceitos:
        print(f"\n🔬 Minerando: {conceito}")
        candidatos = miner.extract_candidates(conceito, "ciencia", max_relacoes=10)
        print(f"   → {len(candidatos)} candidatos extraídos")
        
        if verbose and candidatos:
            for i, cand in enumerate(candidatos[:3], 1):
                print(f"      {i}. {cand.termo_destino} ({cand.tipo})")
                print(f"         Confiança: {cand.confianca:.2f}")
    
    print("\n⚠️  ATENÇÃO: Candidatos estão em QUARENTENA")
    print("   Para validar: /quarentena listar")
    print("   Para aprovar: /quarentena aprovar <conceito> <id>")

def test_extraction_api():
    """Testa extração com API real (se configurada)"""
    print("\n" + "=" * 60)
    print("TESTE 4: Extração com API Real")
    print("=" * 60)
    
    miner = KnowledgeMiner()
    
    if not miner.client:
        print("⏭️  Pulando (API não configurada)")
        return None
    
    try:
        print("🔬 Extraindo relações para 'energia' (campo: fisica)...")
        candidatos = miner.extract_candidates(
            conceito_raiz="energia",
            contexto="fisica",
            max_relacoes=3
        )
        
        print(f"\n📊 Resultados da API:")
        print(f"   Total: {len(candidatos)} candidatos")
        
        for i, c in enumerate(candidatos, 1):
            print(f"\n   [{i}] {c.de} --[{c.tipo}]--> {c.para}")
            print(f"       Confiança: {c.confianca:.2f}")
            print(f"       Evidência: {c.evidencia}")
            print(f"       Timestamp: {c.timestamp}")
        
        print("\n✅ Extração com API funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na extração com API: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quarantine_files():
    """Testa se arquivos de quarentena foram criados"""
    print("\n" + 6: Arquivos de Quarentena")
    print("=" * 60)
    
    from pathlib import Path
    
    quarentena_dir = Path("./data/quarentena")
    
    if not quarentena_dir.exists():
        print("❌ Diretório de quarentena não existe")
        return False
    
    arquivos = list(quarentena_dir.glob("*.json"))
    
    if len(arquivos) == 0:
        print("⚠️  Nenhum arquivo de quarentena encontrado")
        print("   (Execute um teste de extração primeiro)")
        return False
    
    print(f"✅ Encontrados {len(arquivos)} arquivo(s) de quarentena:")
    
    import json
    for arquivo in arquivos:
        print(f"\n   📄 {arquivo.name}")
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"      Conceito: {data['conceito_raiz']}")
        print(f"      Status: {data['status']}")
        print(f"      Candidatos: {data['total_candidatos']}")
    
    return True

if __name__ == "__main__":
    print("\n🧪 BATERIA DE TESTES - DEEPSEEK-CODER-V2-LITE\n")
    
    resultados = {
        "Modelo Local Existe": test_model_exists(),
        "Minerador Inicializado": test_miner_initialization(),
        "Dependências": test_dependencies(),
        "Extração Mock": test_extraction_mock(),
        "Extração Modelo Local": test_extraction_local(),
        "Arquivos Quarentena": test_quarantine_files()
    }
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for teste, resultado in resultados.items():
        if resultado is True:
            status = "✅ PASSOU"
        elif resultado is False:
            status = "❌ FALHOU"
        else:
            status = "⏭️  PULADO"
        
        print(f"{status:12} | {teste}")
    
    print("\n" + "=" * 60)
    
    # Contagem
    passou = sum(1 for r in resultados.values() if r is True)
    falhou = sum(1 for r in resultados.values() if r is False)
    pulado = sum(1 for r in resultados.values() if r is None)
    
    print(f"\nResultado: {passou} passou, {falhou} falhou, {pulado} pulado")
    
    if falhou == 0 and pulado == 0:
        print("\n🎉 Todos os testes passaram!")
    elif falhou == 0:
        print(f"\n✅ Testes OK ({pulado} pulado(s) por falta de modelo)
        print("\n🎉 Todos os testes passaram!")
    else:
        print(f"\n⚠️  {falhou} teste(s) falharam")
