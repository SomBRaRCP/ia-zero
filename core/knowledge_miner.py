# core/knowledge_miner.py
"""
Minerador de Conhecimento Estrutural usando DeepSeek-Coder-V2-Lite (local)
Pipeline: Extração → Quarentena → Validação → Colapso no Grafo TRQ

DeepSeek-Coder = microscópio (não cérebro)
Grafo TRQ = lâmina
Antonia (RWKV) = voz

Modelo: deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct (16B)
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CandidatoRelacao:
    """Candidato a relação extraído por DeepSeek (zona de quarentena)"""
    de: str
    para: str
    tipo: str
    confianca: float
    contexto: str
    evidencia: str = ""
    origem: str = "deepseek"
    timestamp: str = ""

class KnowledgeMiner:
    """
    Minerador estrutural de conhecimento.
    
    IMPORTANTE: Este módulo NÃO adiciona nada automaticamente ao grafo.
    Ele apenas gera candidatos para validação humana.
    """
    
    def __init__(self, quarantine_path: str = "./data/quarentena", model_path: Optional[str] = None):
        self.quarantine_path = Path(quarantine_path)
        self.quarantine_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar modelo local
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        
        if model_path is None:
            model_path = "./models/deepseek-coder-v2-lite"
        
        self.model_path = Path(model_path)
        
        if self.model_path.exists():
            print(f"✅ Modelo encontrado em: {self.model_path}")
            print("   (Modelo será carregado na primeira extração)")
        else:
            print(f"⚠️  Modelo não encontrado em: {self.model_path}")
            print("   Execute: python download_deepseek_model.py")
            print("   (Usando modo mock por enquanto)")
        
    def _load_model(self):
        """Carrega o modelo local (lazy loading)."""
        if self.model is not None:
            return  # Já carregado
        
        if not self.model_path.exists():
            print("   ❌ Modelo não encontrado. Use modo mock.")
            return
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            print("   🔄 Carregando DeepSeek-Coder-V2-Lite...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_path),
                trust_remote_code=True
            )
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"   📍 Dispositivo: {device}")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                str(self.model_path),
                trust_remote_code=True,
                torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            print("   ✅ Modelo carregado!")
            
        except ImportError:
            print("   ❌ Bibliotecas faltando. Instale: pip install transformers torch accelerate")
        except Exception as e:
            print(f"   ❌ Erro ao carregar modelo: {e}")
    
    def extract_candidates(
        self,
        conceito_raiz: str,
        contexto: str = "geral",
        max_relacoes: int = 5
    ) -> List[CandidatoRelacao]:
        """
        Extrai candidatos a relações usando DeepSeek-V3.
        
        Args:
            conceito_raiz: Conceito central para explorar
            contexto: Campo semântico (fisica, biologia, filosofia, etc)
            max_relacoes: Máximo de relações a extrair
        
        Returns:
            Lista de candidatos (NÃO adicionados ao grafo)
        """
        print(f"🔬 Minerando relações para '{conceito_raiz}' no campo '{contexto}'...")
        
        # Carrega modelo se necessário (lazy loading)
        if self.model is None and self.model_path.exists():
            self._load_model()
        
        if self.model is not None:
            candidatos = self._extract_with_local_model(conceito_raiz, contexto, max_relacoes)
        else:
            print("   ⚠️  Modelo não disponível, usando mock")
            candidatos = self._extract_mock(conceito_raiz, contexto)
        
        # Salva na zona de quarentena
        self._save_to_quarantine(conceito_raiz, candidatos)
        
        print(f"   Extraídos {len(candidatos)} candidatos → quarentena")
        return candidatos
    
    def _extract_with_local_model(
        self,
        conceito: str,
        contexto: str,
        max_relacoes: int
    ) -> List[CandidatoRelacao]:
        """
        Extrai relações usando o modelo local DeepSeek-Coder-V2-Lite.
        """
        if self.model is None or self.tokenizer is None:
            print("   ❌ Modelo não carregado")
            return []
        
        prompt = self._build_extraction_prompt(conceito, contexto, max_relacoes)
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Você é um extrator de conhecimento estrutural. "
                               "Identifique relações explícitas entre conceitos. "
                               "Retorne APENAS JSON válido, sem texto adicional."
                },
                {"role": "user", "content": prompt}
            ]
            
            inputs = self.tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(self.model.device)
            
            print("   🔄 Gerando extração...")
            outputs = self.model.generate(
                inputs,
                max_new_tokens=2000,
                temperature=0.1,
                do_sample=True,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            raw_output = self.tokenizer.decode(
                outputs[0][inputs.shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            return self._parse_api_response(raw_output, contexto)
            
        except Exception as e:
            print(f"   ❌ Erro na extração: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_api_response(self, raw: str, contexto: str) -> List[CandidatoRelacao]:
        """
        Parseia a resposta JSON da API.
        """
        try:
            # Remove markdown code blocks se presentes
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            
            data = json.loads(raw)
            candidatos = []
            
            for rel in data.get("relacoes", data if isinstance(data, list) else []):
                candidatos.append(CandidatoRelacao(
                    de=rel["de"],
                    para=rel["para"],
                    tipo=rel["tipo"],
                    confianca=float(rel.get("confianca", 0.7)),
                    contexto=contexto,
                    evidencia=rel.get("evidencia", ""),
                    timestamp=datetime.now().isoformat(),
                    origem="deepseek-api"
                ))
            
            return candidatos
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Erro ao parsear JSON: {e}")
            print(f"   Raw response: {raw[:200]}...")
            return []
        except Exception as e:
            print(f"   ❌ Erro ao processar resposta: {e}")
            return []
    
    def _build_extraction_prompt(self, conceito: str, contexto: str, max_relacoes: int) -> str:
        """Constrói prompt estruturado para extração."""
        return f"""Analise o conceito "{conceito}" no campo "{contexto}".

Identifique relações estruturais explícitas com outros conceitos.

Tipos de relação permitidos:
- definicao: X é definido como Y
- parte_de: X é parte de Y
- causa: X causa Y
- relacionado: X está relacionado a Y (genérico)
- exemplo: X é exemplo de Y

Retorne JSON no formato:
[
  {{
    "de": "conceito_origem",
    "para": "conceito_destino",
    "tipo": "tipo_relacao",
    "confianca": 0.0-1.0,
    "evidencia": "texto que justifica a relação"
  }}
]

Critérios:
1. APENAS relações explícitas e verificáveis
2. confianca = quão certo você está (0.0 a 1.0)
3. evidencia = citação ou raciocínio
4. NO MÁXIMO {max_relacoes} relações mais relevantes
5. SEM especulação ou filosofia
6. SEM relações óbvias demais

Responda APENAS com o JSON, sem texto adicional."""
    
    def _extract_mock(self, conceito: str, contexto: str) -> List[CandidatoRelacao]:
        """Mock de extração (fallback quando API não disponível)"""
        return [
            CandidatoRelacao(
                de=conceito,
                para="trabalho",
                tipo="definicao",
                confianca=0.95,
                contexto=contexto,
                evidencia="Energia é a capacidade de realizar trabalho",
                timestamp=datetime.now().isoformat(),
                origem="mock"
            ),
            CandidatoRelacao(
                de=conceito,
                para="movimento",
                tipo="causa",
                confianca=0.85,
                contexto=contexto,
                evidencia="Energia pode causar movimento em sistemas físicos",
                timestamp=datetime.now().isoformat(),
                origem="mock"
            )
        ]
    
    def _save_to_quarantine(self, conceito: str, candidatos: List[CandidatoRelacao]):
        """Salva candidatos na zona de quarentena para validação humana."""
        quarantine_file = self.quarantine_path / f"quarentena_{conceito}.json"
        
        data = {
            "conceito_raiz": conceito,
            "timestamp": datetime.now().isoformat(),
            "total_candidatos": len(candidatos),
            "status": "aguardando_validacao",
            "candidatos": [
                {
                    "de": c.de,
                    "para": c.para,
                    "tipo": c.tipo,
                    "confianca": c.confianca,
                    "contexto": c.contexto,
                    "evidencia": c.evidencia,
                    "timestamp": c.timestamp,
                    "origem": c.origem,
                    "validado": False,
                    "acao": None  # aceitar|rejeitar|modificar
                }
                for c in candidatos
            ]
        }
        
        quarantine_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        print(f"💾 {len(candidatos)} candidatos salvos em quarentena:")
        print(f"   {quarantine_file}")
    
    def list_quarantine(self) -> List[str]:
        """Lista arquivos na zona de quarentena."""
        if not self.quarantine_path.exists():
            return []
        return [f.name for f in self.quarantine_path.glob("quarentena_*.json")]
    
    def load_quarantine(self, conceito: str) -> Optional[Dict]:
        """Carrega candidatos da quarentena para validação."""
        quarantine_file = self.quarantine_path / f"quarentena_{conceito}.json"
        if not quarantine_file.exists():
            return None
        return json.loads(quarantine_file.read_text(encoding="utf-8"))
    
    def validate_candidate(
        self,
        conceito: str,
        index: int,
        acao: str,
        modificacoes: Optional[Dict] = None
    ) -> bool:
        """
        Valida um candidato específico.
        
        Args:
            conceito: Conceito raiz
            index: Índice do candidato
            acao: 'aceitar', 'rejeitar' ou 'modificar'
            modificacoes: Dict com campos modificados (se acao='modificar')
        
        Returns:
            True se validação foi registrada
        """
        data = self.load_quarantine(conceito)
        if not data or index >= len(data["candidatos"]):
            return False
        
        data["candidatos"][index]["validado"] = True
        data["candidatos"][index]["acao"] = acao
        
        if acao == "modificar" and modificacoes:
            for k, v in modificacoes.items():
                if k in data["candidatos"][index]:
                    data["candidatos"][index][k] = v
        
        # Atualiza status
        total = len(data["candidatos"])
        validados = sum(1 for c in data["candidatos"] if c["validado"])
        data["status"] = f"validados_{validados}/{total}"
        
        quarantine_file = self.quarantine_path / f"quarentena_{conceito}.json"
        quarantine_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        return True
    
    def export_validated(self, conceito: str) -> List[Dict]:
        """
        Exporta apenas candidatos aceitos para adição ao grafo.
        
        Returns:
            Lista de relações prontas para colapso no TRQ Graph
        """
        data = self.load_quarantine(conceito)
        if not data:
            return []
        
        aceitos = [
            {
                "de": c["de"],
                "para": c["para"],
                "tipo": c["tipo"],
                "peso": c["confianca"],
                "origem": "deepseek_validado"
            }
            for c in data["candidatos"]
            if c.get("validado") and c.get("acao") == "aceitar"
        ]
        
        return aceitos


# Funções helper para uso direto

def extrair_conhecimento(conceito: str, contexto: str = "geral") -> int:
    """
    Extrai candidatos de conhecimento para um conceito.
    Retorna número de candidatos extraídos.
    """
    miner = KnowledgeMiner("data/quarentena")
    candidatos = miner.extract_candidates(conceito, contexto)
    print(f"\n🔬 Mineração estrutural concluída:")
    print(f"   Conceito: {conceito}")
    print(f"   Contexto: {contexto}")
    print(f"   Candidatos: {len(candidatos)}")
    print(f"\n⚠️  NADA foi adicionado ao grafo automaticamente.")
    print(f"   Use /validar para revisar os candidatos.")
    return len(candidatos)

def listar_quarentena() -> List[str]:
    """Lista todos os arquivos em quarentena."""
    miner = KnowledgeMiner("data/quarentena")
    return miner.list_quarantine()
