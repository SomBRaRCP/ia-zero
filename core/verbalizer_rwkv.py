# core/verbalizer_rwkv.py
from rwkv.model import RWKV
from rwkv.utils import PIPELINE, PIPELINE_ARGS

class RWKVVerbalizer:
    def __init__(
        self,
        model_path: str,
        strategy: str = "cpu fp32"
    ):
        self.model = RWKV(
            model=model_path,
            strategy=strategy
        )
        self.pipeline = PIPELINE(self.model, "rwkv_vocab_v20230424")

    def verbalize(
        self,
        base_content: str,
        tom: str = "conversacional",
        max_tokens: int = 120
    ) -> str:
        """
        Recebe conteúdo já decidido pela Antonia
        e apenas reescreve de forma fluida.
        """

        prompt = (
            "Tarefa: reformular o texto abaixo de forma clara e educada.\n"
            f"Tom: {tom}\n"
            "Proibições:\n"
            "- Não inventar informações\n"
            "- Não adicionar novos fatos\n"
            "- Não fazer perguntas\n\n"
            "Texto base:\n"
            f"{base_content}\n\n"
            "Texto final:"
        )

        args = PIPELINE_ARGS(
            temperature=0.6,
            top_p=0.9,
            max_tokens=max_tokens
        )

        out = self.pipeline.generate(prompt, args)

        return out.strip()
