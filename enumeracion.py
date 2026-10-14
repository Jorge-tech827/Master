#!/usr/bin/env python3
import subprocess
import requests
import sys
import re
import os
import datetime
import webbrowser
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

# ==========================================
# COLORES PARA LA TERMINAL Y CONOCIMIENTO
# ==========================================
C_RED = '\033[91m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_CYAN = '\033[96m'
C_RESET = '\033[0m'
C_BOLD = '\033[1m'

BASE_CONOCIMIENTO = {
    "21/tcp": {"nombre": "PUERTO 21 (FTP)", "desc": "Transferencia de archivos sin cifrar.", "nivel": "ALTO"},
    "22/tcp": {"nombre": "PUERTO 22 (SSH)", "desc": "Consola remota. Verificar políticas.", "nivel": "MEDIO"},
    "80/tcp": {"nombre": "PUERTO 80 (HTTP)", "desc": "Tráfico web no cifrado. Sensible a intercepción.", "nivel": "ALTO"},
    "443/tcp": {"nombre": "PUERTO 443 (HTTPS)", "desc": "Tráfico web cifrado SSL/TLS.", "nivel": "BAJO"},
    "445/tcp": {"nombre": "PUERTO 445 (SMB)", "desc": "Compartición de archivos. Históricamente crítico.", "nivel": "CRÍTICO"},
    "3306/tcp": {"nombre": "PUERTO 3306 (MySQL)", "desc": "Base de datos expuesta a Internet.", "nivel": "CRÍTICO"},
    "5060/tcp": {"nombre": "PUERTO 5060 (SIP)", "desc": "Centralita VoIP. Riesgo de fraude.", "nivel": "CRÍTICO"},
    "8080/tcp": {"nombre": "PUERTO 8080 (HTTP-Alt)", "desc": "Panel alternativo sin cifrar.", "nivel": "MEDIO"}
}

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def limpiar_ansi(texto):
    return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', texto)

def limpiar_dominio(objetivo):
    if objetivo.startswith("http"): objetivo = urlparse(objetivo).netloc
    return objetivo.split('/')[0]

def exportar_nmap_json(archivo_xml, archivo_json):
    """Lee el XML de Nmap y crea un JSON estructurado."""
    try:
        arbol = ET.parse(archivo_xml)
        raiz = arbol.getroot()
        
        datos_nmap = {"objetivos": []}
        
        for host in raiz.findall('host'):
            info_host = {"ip": "", "puertos": []}
            
            direccion = host.find('address')
            if direccion is not None:
                info_host["ip"] = direccion.get('addr')
            
            puertos = host.find('ports')
            if puertos is not None:
                for puerto in puertos.findall('port'):
                    id_puerto = puerto.get('portid')
                    estado_xml = puerto.find('state')
                    servicio_xml = puerto.find('service')
                    
                    estado = estado_xml.get('state') if estado_xml is not None else "desconocido"
                    servicio = servicio_xml.get('name') if servicio_xml is not None else "desconocido"
                    
                    info_host["puertos"].append({
                        "puerto": id_puerto,
                        "estado": estado,
                        "servicio": servicio
                    })
            
            datos_nmap["objetivos"].append(info_host)
            
        with open(archivo_json, 'w', encoding="utf-8") as f:
            json.dump(datos_nmap, f, indent=4)
            
        print(f"{C_GREEN}[+] Archivo JSON generado: {archivo_json}{C_RESET}")
        
    except Exception as e:
        print(f"{C_RED}[!] Error al convertir a JSON: {e}{C_RESET}")

def ejecutar_comando_cli(comando, archivo_txt):
    print(f"\n{C_CYAN}[*] Ejecutando: {comando}{C_RESET}")
    try:
        res = limpiar_ansi(subprocess.check_output(comando, shell=True, text=True, stderr=subprocess.STDOUT, timeout=60))
        with open(archivo_txt, "a", encoding="utf-8") as f: f.write(f"\n--- {comando} ---\n{res}\n")
        return res
    except Exception as e:
        err = f"[!] Error: {limpiar_ansi(getattr(e, 'output', str(e)))}"
        print(f"{C_RED}{err}{C_RESET}")
        return err

# ==========================================
# GENERACIÓN DE HTML
# ==========================================
def crear_tarjeta_html(titulo, tipo_fase, explicacion, contenido_html):
    clase = "pasiva" if tipo_fase == "Pasiva" else "activa"
    return f'<div class="card {clase}"><div class="card-header"><h3 class="card-title">{titulo}</h3><span class="badge {clase}">Fase: {tipo_fase}</span></div><div class="explicacion-box"><h4>💡 ¿Qué es esto en lenguaje sencillo?</h4><p>{explicacion}</p></div>{contenido_html}</div>'

def generar_html_final(objetivo, bloques_html):
    fecha = datetime.datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
    html_file = f"auditoria_osint_{objetivo.replace('.', '_')}.html"
    css = "<style>:root { --bg-body: #f4f7f6; --bg-card: #ffffff; --primary: #2c3e50; --accent: #3498db; --success: #2ecc71; --warning: #f1c40f; --danger: #e74c3c; } body { font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg-body); color: #333; padding: 20px; } .container { max-width: 1100px; margin: 0 auto; } .header { background: var(--primary); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; border-bottom: 5px solid var(--accent); } .card { background: var(--bg-card); border-radius: 10px; padding: 25px; margin-bottom: 25px; box-shadow: 0 3px 10px rgba(0,0,0,0.08); border-left: 6px solid #ccc; } .card.pasiva { border-left-color: var(--success); } .card.activa { border-left-color: var(--danger); } .card-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; } .card-title { font-size: 1.4em; color: var(--primary); margin: 0; } .explicacion-box { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; margin-bottom: 20px; font-size: 0.95em; } .explicacion-box h4 { margin: 0 0 10px 0; color: var(--accent); } table { width: 100%; border-collapse: collapse; font-size: 0.95em; } th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; } th { background: #f1f5f9; color: var(--primary); } pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; } .badge { padding: 5px 10px; border-radius: 20px; font-size: 0.8em; font-weight: bold; color: white; } .badge.pasiva, .badge.ok { background: var(--success); } .badge.activa, .badge.critical { background: var(--danger); } .badge.warning { background: var(--warning); color: #333; }</style>"
    html = f"<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'><title>Auditoría OSINT - {objetivo}</title>{css}</head><body><div class='container'><div class='header'><h1>🛡️ Informe de Auditoría y Huella Digital</h1><p><strong>Objetivo:</strong> {objetivo}</p><p><strong>Fecha:</strong> {fecha}</p></div>{''.join(bloques_html)}</div></body></html>"
    with open(html_file, "w", encoding="utf-8") as f: f.write(html)
    return html_file

# ==========================================
# BUCLE PRINCIPAL
# ==========================================
def main():
    print(f"\n{C_BOLD}{C_CYAN}=== HERRAMIENTA DE ENUMERACIÓN OSINT ==={C_RESET}")
    obj_raw = input(f"{C_BOLD}Introduce el dominio objetivo (ej. scanme.nmap.org): {C_RESET}").strip()
    if not obj_raw: sys.exit(0)
    objetivo = limpiar_dominio(obj_raw)
    
    print(f"\nFases disponibles:")
    print("1. Pasiva (WHOIS, crt.sh)")
    print("2. Activa (DNS, WhatWeb, Nmap)")
    print("3. Ambas")
    opc = input(f"{C_BOLD}Selecciona una opción (1/2/3): {C_RESET}").strip()
    
    txt_file = f"informe_{objetivo.replace('.', '_')}.txt"
    bloques = []
    with open(txt_file, "w", encoding="utf-8") as f: f.write(f"=== INFORME PARA {objetivo} ===\n")

    if opc in ['1', '3']:
        print(f"\n{C_GREEN}=== INICIANDO FASE PASIVA ==={C_RESET}")
        res_whois = ejecutar_comando_cli(f"whois {objetivo}", txt_file)
        bloques.append(crear_tarjeta_html("1. Identidad Legal (WHOIS)", "Pasiva", "Consulta el Registro oficial del dominio sin alertar al objetivo.", f"<pre>{res_whois}</pre>"))

        print(f"\n{C_CYAN}[*] Consultando crt.sh...{C_RESET}")
        try:
            r = requests.get(f"https://crt.sh/?q={objetivo}&output=json", timeout=15)
            if r.status_code == 200 and r.text.strip():
                subs = set([e['name_value'] for e in r.json()])
                for s in subs: print(f"{C_GREEN}[+] {s}{C_RESET}")
                bloques.append(crear_tarjeta_html("2. Mapa DNS Pasivo (crt.sh)", "Pasiva", "Descubre subdominios ocultos en bases de certificados.", f"<pre>{chr(10).join(['[+] ' + s for s in subs])}</pre>"))
            else: print(f"{C_YELLOW}[-] No se encontraron datos en crt.sh{C_RESET}")
        except Exception as e: print(f"{C_RED}[-] Error con crt.sh: {e}{C_RESET}")

    if opc in ['2', '3']:
        print(f"\n{C_RED}=== INICIANDO FASE ACTIVA ==={C_RESET}")
        res_dig = ejecutar_comando_cli(f"dig {objetivo}", txt_file)
        bloques.append(crear_tarjeta_html("3. Registros DNS (Dig)", "Activa", "Interroga los servidores DNS para confirmar IPs.", f"<pre>{res_dig}</pre>"))
        
        res_what = ejecutar_comando_cli(f"whatweb {objetivo}", txt_file)
        bloques.append(crear_tarjeta_html("4. Huella Tecnológica (WhatWeb)", "Activa", "Analiza la web para descubrir tecnologías y CMS.", f"<pre>{res_what}</pre>"))

        # Preparación de archivos Nmap exportados
        obj_limpio = objetivo.replace('.', '_')
        archivo_og = f"nmap_{obj_limpio}.og"
        archivo_xml = f"nmap_{obj_limpio}.xml"
        archivo_json = f"nmap_{obj_limpio}.json"

        # Ejecución de Nmap con exportaciones
        comando_nmap = f"nmap -sV -F -oG {archivo_og} -oX {archivo_xml} {objetivo}"
        res_nmap = ejecutar_comando_cli(comando_nmap, txt_file)
        
        print(f"{C_GREEN}[+] Archivo Grepable (oG) generado: {archivo_og}{C_RESET}")
        
        # Conversión de XML a JSON
        if os.path.exists(archivo_xml):
            exportar_nmap_json(archivo_xml, archivo_json)

        # Análisis para el informe HTML en base a la salida estándar de Nmap
        coincidencias = re.compile(r'(\d+/(?:tcp|udp))\s+(\w+)\s+(\S+)').findall(res_nmap)
        
        if coincidencias:
            filas_html = []
            print(f"\n{C_YELLOW}=== RESUMEN DE PUERTOS ==={C_RESET}")
            for p, est, serv in coincidencias:
                info = BASE_CONOCIMIENTO.get(p, {"desc": f"Servicio {serv}.", "nivel": "ALTO" if est == "open" else "BAJO"})
                if info["nivel"] in ["ALTO", "CRÍTICO"]:
                    print(f"{C_RED}[🔴 AUDITAR] {p} - {serv} - {info['desc']}{C_RESET}")
                    badge, aud = "critical", "[🔴 AUDITAR]"
                elif info["nivel"] == "MEDIO":
                    print(f"{C_YELLOW}[🟡 REVISAR] {p} - {serv} - {info['desc']}{C_RESET}")
                    badge, aud = "warning", "[🟡 REVISAR]"
                else:
                    print(f"{C_GREEN}[🟢 OK] {p} - {serv} - {info['desc']}{C_RESET}")
                    badge, aud = "ok", "[🟢 OK]"
                filas_html.append(f"<tr><td><b>{p}</b></td><td>{est}</td><td>{serv}</td><td><span class='badge {badge}'>{aud}</span></td><td>{info['desc']}</td></tr>")
            
            bloques.append(crear_tarjeta_html("5. Escaneo de Puertos (Nmap)", "Activa", "Puertos abiertos en el servidor.", f"<table><tr><th>Puerto</th><th>Estado</th><th>Servicio</th><th>Auditoría</th><th>Descripción</th></tr>{''.join(filas_html)}</table>"))

    html_path = generar_html_final(objetivo, bloques)
    print(f"\n{C_GREEN}[+] ¡Terminado! Informe HTML generado en: {html_path}{C_RESET}")
    try: webbrowser.open('file://' + os.path.realpath(html_path))
    except: pass

if __name__ == '__main__': 
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C_RED}[*] Interrumpido por el usuario. Saliendo...{C_RESET}")
        sys.exit(0)
