from core.session_store import create_session, set_profile
from core.engine import SofiaZero

def main():
    print("SofiaZero (IA simbólica) — modo local")
    print("Comandos: /profile <conversacional|exploratorio|trq_duro|debug> | /add palavra | classe | definicao | /exit\n")

    session = create_session(escopo_memoria="user:reginaldo", profile_id="conversacional")
    bot = SofiaZero()

    while True:
        user = input("Você> ").strip()
        if not user:
            continue

        if user.lower() in ("/exit", "/quit"):
            print("Sofia> Até mais.")
            break

        if user.startswith("/profile"):
            parts = user.split()
            if len(parts) >= 2:
                pid = parts[1].strip()
                ok = set_profile(session.session_id, pid)
                print("Sofia>", "Profile alterado." if ok else "Profile inválido.")
            else:
                print("Sofia> Use: /profile conversacional | exploratorio | trq_duro | debug")
            continue

        resp = bot.answer(user, session.session_id)
        print("Sofia>", resp)
        print()

if __name__ == "__main__":
    main()
