import socket
import threading
import sys
import pickle
import os

listado = '/home/josexit/Escritorio/chat_cmd/files'

class Cliente():
    def __init__(self, host="localhost", port=5000):
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((str(host), int(port)))

        msg_recv = threading.Thread(target=self.msg_recv)

        msg_recv.daemon = True
        msg_recv.start()

        while True:
            msg = input('->')
            if msg == 'ls':
                self.list_files()
            elif msg.startswith("get "):
                self.send_msg(msg)
            elif msg == 'salir':
                self.sock.close()
                sys.exit()
            else:
                self.send_msg(msg)

    def msg_recv(self):

        while True:
            try:
                data = self.sock.recv(12048)
                if data:
                    try:
                        msg = pickle.loads(data)
                        if msg == "start_file_transfer":
                        # Recibir el nombre del archivo
                            filename_data = self.sock.recv(12048)
                            filename = pickle.loads(filename_data)
                        
                        # Recibir el tamaño del archivo
                            filesize_data = self.sock.recv(12048)
                            filesize = pickle.loads(filesize_data)

                            print(f'Iniciando descarga de {filename} de {filesize} bytes')
                        
                        # Iniciar la descarga del archivo
                            self.recive_file(filename, filesize)
                        else:
                            print(msg)
                    except pickle.UnpicklingError:
                        print(f"Error al deserializar el mensaje.")
                        pass
            except Exception as e:
                print(f"Error al recibir datos: {e}")
                self.sock.close()
                break

    def recive_file(self, filename, filesize):
        download = 'download'
        if not os.path.exists(download):
            os.makedirs(download)

        # Guardar con el nombre de archivo recibido
        filepath = os.path.join(download, filename)
        bytes_recibidos = 0

        with open(filepath, 'wb') as f:
            while bytes_recibidos < filesize:
                chunk = self.sock.recv(12048)
                if not chunk:
                    break
                f.write(chunk)
                bytes_recibidos += len(chunk)
                print(f"Recibido {bytes_recibidos} de {filesize} bytes", end='\r')

            print(f"\nArchivo guardado en '{filepath}'")

    def list_files(self):
        try:
            with os.scandir(listado) as contenidos:
                print("Archivos en el directorio 'files':")
                for contenido in contenidos:
                    print(contenido.name)
        except FileNotFoundError:
            print(f"El directorio {listado} no existe.")
        except Exception as e:
            print(f"Error al listar los archivos: {e}")

    def send_msg(self, msg):
        self.sock.send(pickle.dumps(msg))


c = Cliente()
