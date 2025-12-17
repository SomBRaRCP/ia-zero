from core.session_store import create_session, set_profile
from core.engine import Antonia

def main():
    print("Antonia — IA simbólica (modo local)")
    print("Comandos:")
    print("  /add palavra | classe | definicao - Ensinar nova palavra")
    print("  /relacionar conceito1 | conceito2 | tipo - Criar relação no grafo")
    print("  /graph stats - Estatísticas do grafo TRQ")
    print("  /graph ver <conceito> - Ver nó e relações")
    print("  /profile <nome> - Mudar perfil (conversacional|exploratorio|trq_duro|debug)")
    print("  /exit - Sair\n")

    session = create_session(escopo_memoria="user:reginaldo", profile_id="conversacional")
    bot = Antonia()

    while True:
        user = input("Você> ").strip()
        if not user:
            continue

        if user.lower() in ("/exit", "/quit"):
            print("Antonia> Até mais.")
            break

        if user.startswith("/profile"):
            parts = user.split()
            if len(parts) >= 2:
                pid = parts[1].strip()
                ok = set_profile(session.session_id, pid)
                print("Antonia>", "Profile alterado." if ok else "Profile inválido.")
            else:
                print("Antonia> Use: /profile conversacional | exploratorio | trq_duro | debug")
            continue

        resp = bot.answer(user, session.session_id)
        print("Antonia>", resp)
        print()

if __name__ == "__main__":
    main()
