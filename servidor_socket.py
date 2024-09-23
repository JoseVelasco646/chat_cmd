import socket
import threading
import sys
import pickle
import os

directorio_archivos = '/home/josexit/Escritorio/chat_cmd/files'

class Servidor():
    def __init__(self, host="localhost", port=5000):
        self.clientes = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((str(host), int(port)))
        self.sock.listen(10)
        self.sock.setblocking(False)

        aceptar = threading.Thread(target=self.aceptarCon)
        procesar = threading.Thread(target=self.procesarCon)
        
        aceptar.daemon = True
        aceptar.start()

        procesar.daemon = True
        procesar.start()

        while True:
            msg = input('->')
            if msg == 'salir':
                self.sock.close()
                sys.exit()
            else:
                pass

    def msg_to_all(self, msg, cliente):
        for c in self.clientes:
            try:
                if c != cliente:
                    c.send(msg)
            except:
                self.clientes.remove(c)

    def aceptarCon(self):
        print("AceptarCon iniciado")
        while True:
            try:
                conn, addr = self.sock.accept()
                conn.setblocking(False)
                self.clientes.append(conn)
            except:
                pass

    def procesarCon(self):
        print("ProcesarCon iniciado")
        while True:
            if len(self.clientes) > 0:
                for c in self.clientes:
                    try:
                        data = c.recv(1024)
                        if data:
                            msg = pickle.loads(data)
                            print(f"Mensaje recibido: {msg}")
                            if msg.startswith("get "):
                                archivo = msg.split()[1]
                                self.enviar_archivo(c, archivo)
                            else:
                                self.msg_to_all(data, c)
                    except:
                        pass

    def enviar_archivo(self, client_socket, filename):
        # Construir la ruta completa del archivo
        filepath = os.path.join(directorio_archivos, filename)

        # Verificar si el archivo existe
        if not os.path.isfile(filepath):
            client_socket.send(pickle.dumps(f"Error: El archivo '{filename}' no existe."))
            return

        try:
            # Enviar la señal de inicio de transferencia
            client_socket.send(pickle.dumps("start_file_transfer"))

            # Enviar el nombre del archivo
            client_socket.send(pickle.dumps(filename))

            # Obtener el tamaño del archivo y enviarlo
            filesize = os.path.getsize(filepath)
            client_socket.send(pickle.dumps(filesize))

            # Enviar el archivo en bloques
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(12048)
                    if not chunk:
                        break
                    client_socket.send(chunk)
            print(f"Archivo '{filename}' enviado correctamente.")
        except Exception as e:
            print(f"Error al enviar el archivo: {e}")


s = Servidor()
