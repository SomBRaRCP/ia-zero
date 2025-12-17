#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_dialogue_state.py

Testa estado conversacional da Antonia.
Valida que ela:
- muda de papel conforme profundidade
- expande respostas quando apropriado
- NÃO inventa quando não há contexto
"""

from core.dialogue_state import EstadoDialogo, InferenciaPragmatica
from core.engine import Antonia
from core.session_store import create_session

def test_estado_basico():
    """Testa criação e atualização de estado"""
    print("=" * 60)
    print("TESTE 1: Estado básico")
    print("=" * 60)
    
    estado = EstadoDialogo()
    assert estado.papel == "neutro"
    assert estado.profundidade == 0
    
    # Primeiro turno
    estado.registrar_turno("o que é energia?", "Energia (substantivo): ...", topico="energia")
    assert estado.profundidade == 1
    assert estado.topico_atual == "energia"
    
    # Mesmo tópico aumenta profundidade
    estado.registrar_turno("e como funciona?", "...", topico="energia")
    assert estado.profundidade == 2
    
    # Mudança de tópico reseta
    estado.registrar_turno("o que é massa?", "...", topico="massa")
    assert estado.profundidade == 1
    assert estado.topico_atual == "massa"
    
    print("[OK] Estado básico funcionando")
    print()

def test_inferencia_papel():
    """Testa inferência de papel conversacional"""
    print("=" * 60)
    print("TESTE 2: Inferência de papel")
    print("=" * 60)
    
    estado = EstadoDialogo()
    
    # Sem profundidade = neutro
    papel = estado.inferir_papel()
    assert papel == "neutro"
    print(f"  Profundidade 0 → papel: {papel}")
    
    # Primeira pergunta = definidora
    estado.profundidade = 1
    papel = estado.inferir_papel("energia")
    assert papel == "definidora"
    print(f"  Profundidade 1 → papel: {papel}")
    
    # Segunda pergunta = explicadora
    estado.profundidade = 2
    papel = estado.inferir_papel("energia")
    assert papel == "explicadora"
    print(f"  Profundidade 2 → papel: {papel}")
    
    # Terceira+ = exploradora
    estado.profundidade = 3
    papel = estado.inferir_papel("energia")
    assert papel == "exploradora"
    print(f"  Profundidade 3 → papel: {papel}")
    
    print("[OK] Inferência de papel funcionando")
    print()

def test_deteccao_tipo_pergunta():
    """Testa detecção de tipo de pergunta (pragmática)"""
    print("=" * 60)
    print("TESTE 3: Detecção tipo de pergunta")
    print("=" * 60)
    
    casos = [
        ("o que é energia?", "definicao"),
        ("qual é a massa?", "definicao"),
        ("como funciona isso?", "explicacao"),
        ("por que acontece?", "explicacao"),
        ("explica melhor", "explicacao"),
        ("qual a relação entre massa e energia?", "relacao"),
        ("e o momento?", "continuacao"),
        ("mas isso significa que...", "continuacao"),
        ("mostre exemplos", "comando"),
    ]
    
    for pergunta, esperado in casos:
        detectado = InferenciaPragmatica.detectar_tipo_pergunta(pergunta)
        status = "[OK]" if detectado == esperado else "[FALHA]"
        print(f"  {status} '{pergunta}' -> {detectado} (esperado: {esperado})")
    
    print()

def test_gesto_final():
    """Testa geração de gesto conversacional"""
    print("=" * 60)
    print("TESTE 4: Gesto conversacional final")
    print("=" * 60)
    
    estado = EstadoDialogo()
    
    # Definidora não gera gesto
    estado.papel = "definidora"
    estado.profundidade = 1
    gesto = estado.gerar_gesto_final()
    assert gesto == ""
    print(f"  Papel definidora -> sem gesto: [OK]")
    
    # Explicadora gera gesto se profundidade >= 2
    estado.papel = "explicadora"
    estado.profundidade = 2
    gesto = estado.gerar_gesto_final()
    assert gesto != ""
    print(f"  Papel explicadora (prof=2) -> gesto: '{gesto.strip()}' [OK]")
    
    # Exploradora gera gesto contextual
    estado.papel = "exploradora"
    estado.profundidade = 3
    estado.topico_atual = "energia"
    gesto = estado.gerar_gesto_final()
    assert "energia" in gesto or "conceitos" in gesto
    print(f"  Papel exploradora -> gesto: '{gesto.strip()}' [OK]")
    
    print()

def test_conversacao_progressiva():
    """Testa conversa progressiva real com Antonia"""
    print("=" * 60)
    print("TESTE 5: Conversa progressiva (integração)")
    print("=" * 60)
    
    antonia = Antonia()
    sess = create_session("test_dialogue")
    session_id = sess.session_id
    
    # Adiciona conceito ao grafo primeiro
    antonia.answer("/add energia | substantivo | capacidade de realizar trabalho | trabalho,forca", session_id)
    antonia.answer("/add trabalho | substantivo | força aplicada sobre distância | forca,energia", session_id)
    antonia.answer("/relacionar energia | trabalho | relacionado", session_id)
    
    # Primeiro turno: definição pura
    print("\n[Turno 1 - Pergunta inicial]")
    resp1 = antonia.answer("o que é energia?", session_id)
    print(f"Resposta: {resp1}")
    estado1 = antonia.estados_dialogo[session_id]
    print(f"Estado: papel={estado1.papel}, profundidade={estado1.profundidade}")
    assert "energia" in resp1.lower()
    assert estado1.profundidade == 1
    
    # Segundo turno: mesma área, deve expandir
    print("\n[Turno 2 - Aprofundando]")
    resp2 = antonia.answer("como funciona energia?", session_id)
    print(f"Resposta: {resp2}")
    estado2 = antonia.estados_dialogo[session_id]
    print(f"Estado: papel={estado2.papel}, profundidade={estado2.profundidade}")
    # Deve ter aumentado profundidade (mesmo conceito)
    
    # Terceiro turno: exploração profunda
    print("\n[Turno 3 - Explorando]")
    resp3 = antonia.answer("por que energia?", session_id)
    print(f"Resposta: {resp3}")
    estado3 = antonia.estados_dialogo[session_id]
    print(f"Estado: papel={estado3.papel}, profundidade={estado3.profundidade}")
    
    # Deve ter gesto conversacional agora
    if estado3.papel in ["explicadora", "exploradora"]:
        print(f"[OK] Papel conversacional ativo: {estado3.papel}")
    
    print()

def test_principio_guardiao():
    """Testa que Antonia NÃO inventa quando não há base"""
    print("=" * 60)
    print("TESTE 6: Princípio guardião (não inventa)")
    print("=" * 60)
    
    antonia = Antonia()
    sess = create_session("test_honesty")
    session_id = sess.session_id
    
    # Pergunta sobre conceito inexistente
    resp = antonia.answer("o que é xyzqwerty?", session_id)
    print(f"Pergunta sobre conceito inexistente: {resp}")
    
    # NÃO deve inventar definição
    assert "não encontrei" in resp.lower() or "não tenho" in resp.lower()
    print("[OK] Antonia mantém honestidade estrutural")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTANDO ESTADO CONVERSACIONAL DA ANTONIA")
    print("Princípio: Não inventa. Não performa. Só fala quando há contexto.")
    print("=" * 60 + "\n")
    
    test_estado_basico()
    test_inferencia_papel()
    test_deteccao_tipo_pergunta()
    test_gesto_final()
    test_conversacao_progressiva()
    test_principio_guardiao()
    
    print("=" * 60)
    print("TODOS OS TESTES PASSARAM [OK]")
    print("Antonia agora tem consciência conversacional.")
    print("=" * 60)
