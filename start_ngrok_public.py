#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicia servidor web + ngrok e abre navegador no link público
"""

import subprocess
import time
import webbrowser
import requests
import sys
from pathlib import Path

PORT = 8000
NGROK_API = "http://localhost:4040/api/tunnels"

def get_ngrok_url(max_attempts=10, delay=1):
    """Aguarda ngrok iniciar e retorna URL pública"""
    print("Aguardando ngrok gerar link público...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(NGROK_API, timeout=2)
            if response.ok:
                tunnels = response.json().get("tunnels", [])
                for tunnel in tunnels:
                    if tunnel.get("proto") == "https":
                        url = tunnel.get("public_url")
                        if url:
                            return url
        except:
            pass
        
        time.sleep(delay)
    
    return None

def main():
    print("=" * 70)
    print("ANTONIA - SERVIDOR WEB PÚBLICO")
    print("=" * 70)
    
    # Inicia ngrok em background
    print(f"\n1. Iniciando ngrok na porta {PORT}...")
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", str(PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    
    # Aguarda e pega URL pública
    public_url = get_ngrok_url()
    
    if not public_url:
        print("\n❌ Erro: Não foi possível obter URL pública do ngrok")
        print("   Verifique se ngrok está instalado e configurado")
        ngrok_process.terminate()
        return
    
    print(f"\n✅ Link público gerado: {public_url}")
    print("\n2. Abrindo navegador...")
    
    # Abre navegador
    webbrowser.open(public_url)
    
    print(f"\n3. Iniciando servidor FastAPI na porta {PORT}...")
    print(f"\n{'='*70}")
    print(f"🌐 Acesse: {public_url}")
    print(f"📡 Servidor local: http://localhost:{PORT}")
    print(f"{'='*70}")
    print("\nPressione Ctrl+C para encerrar\n")
    
    # Inicia uvicorn (bloqueia aqui)
    try:
        subprocess.run([
            "uvicorn",
            "web_server:app",
            "--host", "0.0.0.0",
            "--port", str(PORT)
        ])
    except KeyboardInterrupt:
        print("\n\nEncerrando servidor...")
    finally:
        ngrok_process.terminate()
        print("Ngrok encerrado.")

if __name__ == "__main__":
    main()
