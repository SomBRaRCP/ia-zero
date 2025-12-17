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


def resposta_exemplo(subject: str, exemplos: list[str]) -> str:
    if not exemplos:
        return (
            f'Exemplo em frase: "Eu preciso de {subject}."\n'
            f'\nSe quiser me ensinar exemplos melhores: /relacionar {subject} | <exemplo> | exemplo'
        )
    return "**Exemplos:**\n" + "\n".join([f"- {x}" for x in exemplos])


def resposta_ensinar_ok(palavra: str) -> str:
    return f"Registrado. Agora eu sei **{palavra}**."

def resposta_ensinar_uso() -> str:
    return "Use: /add palavra | classe | definicao (opcional: | rel1,rel2)"

def resposta_meta_conversa(profile_id: str) -> str:
    return (
        "Sim — eu consigo conversar, mas sem inventar.\n"
        f"Seu profile atual é **{profile_id}**.\n\n"
        "Para eu conversar melhor, faça 2 ou 3 perguntas no mesmo tema (eu mantenho o tópico).\n"
        "Se quiser um diálogo mais fluido, use: /profile conversacional\n"
        "Se quiser rigor e zero especulação: /profile trq_duro"
    )


def resposta_saudacao() -> str:
    return "Oi! Quer seguir em TI ou Fisica agora? Se me disser o tema, eu puxo o melhor caminho."


def resposta_despedida() -> str:
    return "Beleza. Ate mais."


def resposta_agradecimento() -> str:
    return "De nada. Quer continuar no mesmo tema ou mudar de assunto?"


def resposta_confirmacao(topico: str | None = None) -> str:
    if topico:
        return f"Certo. Quer continuar em **{topico}** ou mudar de tema?"
    return "Certo. Quer continuar no mesmo tema ou mudar de assunto?"


def resposta_afirmacao(topico: str | None = None) -> str:
    if topico:
        return f"Perfeito. Sigo em **{topico}**: o que voce quer ver agora (definicao, exemplos, ou relacoes)?"
    return "Perfeito. Manda a proxima pergunta."


def resposta_negacao(topico: str | None = None) -> str:
    if topico:
        return f"Beleza. Entao mudamos de rota. Quer continuar em **{topico}** por outro angulo, ou trocar de tema?"
    return "Tudo bem. O que voce quer fazer entao?"
