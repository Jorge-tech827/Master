#!/usr/bin/env python3
import requests
import sys
import os
import datetime
import webbrowser
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer

C_RED, C_GREEN, C_YELLOW, C_CYAN, C_RESET, C_BOLD = '\033[91m', '\033[92m', '\033[93m', '\033[96m', '\033[0m', '\033[1m'

CABECERAS_SEGURIDAD = {
    "Strict-Transport-Security": {"desc": "Fuerza HTTPS. Previene downgrades.", "nivel": "ALTO"},
    "Content-Security-Policy": {"desc": "Mitiga XSS controlando scripts.", "nivel": "ALTO"},
    "X-Frame-Options": {"desc": "Protege contra Clickjacking.", "nivel": "MEDIO"},
    "X-Content-Type-Options": {"desc": "Previene manipulación MIME.", "nivel": "MEDIO"}
}
CABECERAS_INFO = {"Server": "Fuga: Revela software del servidor.", "X-Powered-By": "Fuga: Revela tecnología backend."}

def generar_html_cabeceras(dominio, filas_html):
    fecha = datetime.datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
    html_file = f"auditoria_cabeceras_{dominio.replace('.', '_')}.html"
    css = "<style>:root { --primary: #2c3e50; --accent: #3498db; --success: #2ecc71; --warning: #f1c40f; --danger: #e74c3c; } body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f4f7f6; color: #333; padding: 20px; } .container { max-width: 1100px; margin: 0 auto; } .header { background: var(--primary); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; border-bottom: 5px solid var(--accent); } .card { background: white; border-radius: 10px; padding: 25px; margin-bottom: 25px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); border-left: 6px solid var(--danger); } .explicacion-box { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; margin-bottom: 20px; font-size: 0.95em; } table { width: 100%; border-collapse: collapse; font-size: 0.95em; } th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; } th { background: #f1f5f9; color: var(--primary); } .badge { padding: 5px 10px; border-radius: 20px; font-size: 0.8em; font-weight: bold; color: white; } .badge.ok { background: var(--success); } .badge.critical { background: var(--danger); } .badge.warning { background: var(--warning); color: #333; }</style>"
    html = f"<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'><title>Cabeceras - {dominio}</title>{css}</head><body><div class='container'><div class='header'><h1>🛡️ Auditoría de Cabeceras HTTP</h1><p><strong>Objetivo:</strong> {dominio}</p><p><strong>Fecha:</strong> {fecha}</p></div><div class='card'><h3>Análisis de Escudos Web</h3><div class='explicacion-box'><h4>💡 ¿Qué es esto en lenguaje sencillo?</h4><p>Comprueba si la web activa medidas exigidas para bloquear hackers.</p></div><table><tr><th>Cabecera</th><th>Estado</th><th>Auditoría</th><th>Descripción</th></tr>{''.join(filas_html)}</table></div></div></body></html>"
    with open(html_file, "w", encoding="utf-8") as f: f.write(html)
    return html_file

def analizar_cabeceras():
    url = input(f"\n{C_BOLD}Introduce la URL (ej. https://ejemplo.com): {C_RESET}").strip()
    if not url: return
    url = "https://" + url if not url.startswith("http") else url
    dominio = urlparse(url).netloc
    
    print(f"\n{C_CYAN}[*] Solicitando cabeceras a {url}...{C_RESET}")
    try: r = requests.get(url, timeout=8, allow_redirects=True)
    except Exception as e: print(f"{C_RED}[!] Error: {e}{C_RESET}"); return

    filas_html = []
    print(f"\n{C_YELLOW}=== AUDITORÍA DE CABECERAS ==={C_RESET}")
    
    for c, info in CABECERAS_SEGURIDAD.items():
        if r.headers.get(c):
            print(f"{C_GREEN}[🟢 OK] {c} configurada.{C_RESET}")
            filas_html.append(f"<tr><td><b>{c}</b></td><td>PRESENTA</td><td><span class='badge ok'>[🟢 OK]</span></td><td>{info['desc']}</td></tr>")
        else:
            if info['nivel'] == "ALTO":
                print(f"{C_RED}[🔴 AUDITAR] Falta {c} - {info['desc']}{C_RESET}")
                filas_html.append(f"<tr><td><b>{c}</b></td><td>NO CONFIGURADA</td><td><span class='badge critical'>[🔴 AUDITAR]</span></td><td>{info['desc']}</td></tr>")
            else:
                print(f"{C_YELLOW}[🟡 REVISAR] Falta {c} - {info['desc']}{C_RESET}")
                filas_html.append(f"<tr><td><b>{c}</b></td><td>NO CONFIGURADA</td><td><span class='badge warning'>[🟡 REVISAR]</span></td><td>{info['desc']}</td></tr>")

    for c, desc in CABECERAS_INFO.items():
        v = r.headers.get(c)
        if v:
            print(f"{C_RED}[🔴 FUGA INFO] {c} expuesta: {v}{C_RESET}")
            filas_html.append(f"<tr style='background:#ffe6e6;'><td><b>{c}</b></td><td>EXPUESTA: {v}</td><td><span class='badge critical'>[🔴 FUGA INFO]</span></td><td>{desc}</td></tr>")

    html_path = generar_html_cabeceras(dominio, filas_html)
    print(f"\n{C_GREEN}[+] ¡Terminado! Informe generado en: {html_path}{C_RESET}")
    try: webbrowser.open('file://' + os.path.realpath(html_path))
    except: pass

class CapturadorHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"\n{C_RED}[🔴 ALERTA] Petición interceptada!{C_RESET}")
        print(f" ┣ {C_BOLD}IP Origen:{C_RESET} {self.client_address[0]}")
        print(f" ┣ {C_BOLD}Path:{C_RESET} {self.path}")
        print(f" ┗ {C_BOLD}User-Agent:{C_RESET} {self.headers.get('User-Agent', 'Desconocido')}")
        
        with open("captura_user_agents.txt", "a") as f:
            f.write(f"[+] IP: {self.client_address[0]} | Path: {self.path} | UA: {self.headers.get('User-Agent')}\n")
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, format, *args): pass

def iniciar_servidor():
    puerto = 8080
    print(f"\n{C_GREEN}[+] Levantando servidor HTTP en puerto {puerto}...{C_RESET}")
    print(f"{C_YELLOW}[*] Esperando conexiones en http://0.0.0.0:{puerto} (Pulsa Ctrl+C para detener){C_RESET}")
    try: HTTPServer(('0.0.0.0', puerto), CapturadorHTTP).serve_forever()
    except KeyboardInterrupt: print(f"\n{C_CYAN}[*] Servidor detenido.{C_RESET}")

def main():
    while True:
        print(f"\n{C_BOLD}{C_CYAN}=== ANÁLISIS DE CABECERAS Y CAPTURA ==={C_RESET}")
        print(f" {C_YELLOW}1.{C_RESET} Auditoría de Cabeceras HTTP")
        print(f" {C_YELLOW}2.{C_RESET} Levantar HTTP Listener (Capturar User-Agent)")
        print(f" {C_YELLOW}0.{C_RESET} Salir\n")
        opc = input(f"{C_BOLD}Selecciona una opción > {C_RESET}").strip()
        
        if opc == '1': analizar_cabeceras()
        elif opc == '2': iniciar_servidor()
        elif opc == '0': sys.exit(0)
        else: print(f"{C_RED}[!] Opción no válida.{C_RESET}")

if __name__ == '__main__': main()
