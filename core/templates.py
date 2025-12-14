def resposta_definicao(palavra: str, definicao: str, classe: str | None = None) -> str:
    if classe:
        return f"**{palavra}** ({classe}): {definicao}"
    return f"**{palavra}**: {definicao}"

def resposta_nao_encontrei(palavra: str) -> str:
    return (
        f"Eu não tenho a definição de **{palavra}** no meu dicionário ainda.\n"
        f"Use /add palavra | classe | definicao (e opcional: | rel1,rel2)."
    )

def resposta_como(subject: str, base: str) -> str:
    return f"Sobre **{subject}**, eu posso responder assim (base):\n{base}"

def resposta_porque(subject: str, base: str) -> str:
    return f"Sobre **{subject}**, uma explicação possível (base):\n{base}"

def resposta_lista(subject: str, itens: list[str]) -> str:
    if not itens:
        return f"Eu não tenho itens cadastrados para **{subject}** ainda."
    return "**Lista:**\n" + "\n".join([f"- {x}" for x in itens])

def resposta_ensinar_ok(palavra: str) -> str:
    return f"Registrado. Agora eu sei **{palavra}**."

def resposta_ensinar_uso() -> str:
    return "Use: /add palavra | classe | definicao (opcional: | rel1,rel2)"
