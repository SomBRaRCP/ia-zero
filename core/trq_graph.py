# core/trq_graph.py
"""
Grafo TRQ - Malha explícita de conceitos (NQCs) e relações.
Conhecimento não é texto, é estrutura.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional

class TRQGraph:
    """
    Grafo TRQ para representação estruturada de conhecimento.
    
    Ontologia mínima:
    - definicao: X é definido por Y
    - parte_de: X compõe Y
    - causa: X provoca Y
    - relacionado: X tem associação semântica com Y
    - exemplo: X é um exemplo de Y
    """
    
    TIPOS_VALIDOS = {"definicao", "parte_de", "causa", "relacionado", "exemplo"}
    
    def __init__(self, path: str):
        self.path = Path(path)
        self.data = {"nodos": {}, "arestas": []}
        self.load()

    def load(self):
        """Carrega grafo do disco se existir."""
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self.data = {"nodos": {}, "arestas": []}

    def save(self):
        """Persiste grafo no disco."""
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def add_node(
        self, 
        node_id: str, 
        definicao: str, 
        regiao: str = "geral",
        origem: str = "humano",
        peso_estabilidade: float = 1.0,
        peso_confianca: float = 1.0,
        *,
        save: bool = True,
    ) -> bool:
        """
        Adiciona nó (NQC) ao grafo.
        
        Args:
            node_id: Identificador único do conceito
            definicao: Definição curta do conceito
            regiao: Regionalidade quântica (campo semântico)
            origem: Fonte do conhecimento (humano, modelo, livro)
            peso_estabilidade: Quanto o conceito é central (0.0 a 1.0)
            peso_confianca: Confiabilidade da origem (0.0 a 1.0)
        
        Returns:
            True se nó foi adicionado, False se já existia
        """
        if node_id not in self.data["nodos"]:
            # Extrai campo e nível da região (formato: "campo:nome:nivel")
            partes_regiao = regiao.split(":")
            regiao_estruturada = {
                "nome": partes_regiao[0] if len(partes_regiao) >= 1 else regiao,
                "campo": partes_regiao[1] if len(partes_regiao) >= 2 else "geral",
                "nivel": int(partes_regiao[2]) if len(partes_regiao) >= 3 else 1
            }
            
            self.data["nodos"][node_id] = {
                "id": node_id,
                "definicao_curta": definicao,
                "peso": {
                    "estabilidade": min(max(peso_estabilidade, 0.0), 1.0),
                    "confianca": min(max(peso_confianca, 0.0), 1.0)
                },
                "origem": origem,
                "regiao": regiao_estruturada
            }
            if save:
                self.save()
            return True
        return False

    def add_edge(
        self, 
        de: str, 
        para: str, 
        tipo: str, 
        peso: float = 0.8, 
        origem: str = "humano",
        bidirecional: bool = False,
        *,
        save: bool = True,
    ) -> bool:
        """
        Adiciona aresta (relação) ao grafo.
        
        Args:
            de: Nó origem
            para: Nó destino
            tipo: Tipo de relação (deve estar em TIPOS_VALIDOS)
            peso: Densidade informacional/estabilidade (0.0 a 1.0)
            origem: Fonte da relação
            bidirecional: Se True, cria relação inversa também
        
        Returns:
            True se aresta foi adicionada, False se tipo inválido
        """
        if tipo not in self.TIPOS_VALIDOS:
            return False
            
        # Garante que ambos os nós existem
        if de not in self.data["nodos"] or para not in self.data["nodos"]:
            return False
            
        self.data["arestas"].append({
            "de": de,
            "para": para,
            "tipo": tipo,
            "peso": min(max(peso, 0.0), 1.0),  # Clamp entre 0 e 1
            "origem": origem
        })
        
        # Adiciona relação inversa se solicitado
        if bidirecional:
            tipo_inverso = self._get_tipo_inverso(tipo)
            self.data["arestas"].append({
                "de": para,
                "para": de,
                "tipo": tipo_inverso,
                "peso": min(max(peso, 0.0), 1.0),
                "origem": origem
            })
        
        if save:
            self.save()
        return True
    
    def _get_tipo_inverso(self, tipo: str) -> str:
        """Retorna o tipo inverso de uma relação."""
        inversos = {
            "definicao": "definido_por",
            "definido_por": "definicao",
            "parte_de": "composto_por",
            "composto_por": "parte_de",
            "causa": "causado_por",
            "causado_por": "causa",
            "relacionado": "relacionado",  # Simétrico
            "exemplo": "exemplificado_por",
            "exemplificado_por": "exemplo"
        }
        return inversos.get(tipo, tipo)

    def get_node(self, node_id: str) -> Optional[Dict]:
        """Retorna nó pelo ID ou None se não existir."""
        return self.data["nodos"].get(node_id)

    def related(self, a: str, b: str) -> List[Dict]:
        """
        Retorna todas as relações entre dois nós.
        
        Args:
            a: ID do primeiro nó
            b: ID do segundo nó
        
        Returns:
            Lista de arestas conectando a e b (em qualquer direção)
        """
        return [
            e for e in self.data["arestas"]
            if (e["de"] == a and e["para"] == b) or (e["de"] == b and e["para"] == a)
        ]

    def neighbors(self, node_id: str, tipo: Optional[str] = None) -> List[str]:
        """
        Retorna vizinhos de um nó.
        
        Args:
            node_id: ID do nó
            tipo: Filtrar por tipo de relação (opcional)
        
        Returns:
            Lista de IDs de nós vizinhos
        """
        vizinhos = []
        for e in self.data["arestas"]:
            if tipo and e["tipo"] != tipo:
                continue
                
            if e["de"] == node_id:
                vizinhos.append(e["para"])
            elif e["para"] == node_id:
                vizinhos.append(e["de"])
                
        return list(set(vizinhos))  # Remove duplicatas

    def get_region(self, regiao: str) -> List[str]:
        """Retorna todos os nós de uma região."""
        return [
            nid for nid, ndata in self.data["nodos"].items()
            if ndata.get("regiao") == regiao
        ]

    def stats(self) -> Dict:
        """Retorna estatísticas do grafo."""
        regioes = set()
        for node in self.data["nodos"].values():
            regiao = node.get("regiao", "geral")
            # regiao pode ser string ou dict {nome, campo, nivel}
            if isinstance(regiao, dict):
                regiao = regiao.get("nome", "geral")
            if regiao:
                regioes.add(regiao)
        
        tipos = set()
        for edge in self.data["arestas"]:
            tipo = edge.get("tipo")
            if tipo:
                tipos.add(tipo)
        
        return {
            "total_nodos": len(self.data["nodos"]),
            "total_arestas": len(self.data["arestas"]),
            "regioes": sorted(list(regioes)),
            "tipos_relacao": sorted(list(tipos))
        }
