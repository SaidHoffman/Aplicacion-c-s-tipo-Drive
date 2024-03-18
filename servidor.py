import socket
import os
import shutil

# Leer las rutas de carpetas desde el archivo "rutas.txt"
with open("rutas.txt", "r") as f:
    rutas = f.read().splitlines()
    ruta_local = rutas[0]
    ruta_remota = rutas[1]

# Crear el socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 1234))
server_socket.listen(5)
print("Servidor escuchando en localhost:1234...")

# Funciones para las operaciones de archivos y carpetas

def listar_remote(conn, ruta_remota):
    """
    Envía al cliente una lista de los archivos y carpetas en la ruta remota actual.

    Args:
        conn (socket.socket): El socket de la conexión con el cliente.
        ruta_remota (str): La ruta remota actual.
    """
    contenido = os.listdir(ruta_remota)
    if not contenido:
        conn.sendall("La carpeta está vacía.".encode('utf-8'))
    else:
        conn.sendall(bytes('\n'.join(contenido), encoding='utf-8'))

def crear_remote(conn, ruta_remota, nueva_carpeta):
    """
    Crea una nueva carpeta en la ruta remota actual y envía al cliente la lista actualizada.

    Args:
        conn (socket.socket): El socket de la conexión con el cliente.
        ruta_remota (str): La ruta remota actual.
        nueva_carpeta (str): El nombre de la nueva carpeta a crear.
    """
    nueva_ruta = os.path.join(ruta_remota, nueva_carpeta)
    try:
        os.makedirs(nueva_ruta)
        listar_remote(conn, ruta_remota)
    except FileExistsError:
        conn.sendall(b"La carpeta ya existe.")

def eliminar_remote(conn, ruta_remota, item):
    """
    Elimina un archivo o carpeta en la ruta remota actual y envía al cliente la lista actualizada.

    Args:
        conn (socket.socket): El socket de la conexión con el cliente.
        ruta_remota (str): La ruta remota actual.
        item (str): El nombre del archivo o carpeta a eliminar.
    """
    ruta_item = os.path.join(ruta_remota, item)
    if os.path.isdir(ruta_item):
        try:
            shutil.rmtree(ruta_item)
            listar_remote(conn, ruta_remota)
        except OSError as e:
            conn.sendall(bytes(f"No se pudo eliminar la carpeta: {e.strerror}", encoding='utf-8'))
    else:
        try:
            os.remove(ruta_item)
            listar_remote(conn, ruta_remota)
        except OSError as e:
            conn.sendall(bytes(f"No se pudo eliminar el archivo: {e.strerror}", encoding='utf-8'))

# Bucle principal del servidor
while True:
    conn, addr = server_socket.accept()
    print(f"Nueva conexión entrante desde {addr}")
    ruta_remota_actual = ruta_remota
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            comando = data.decode('utf-8')
            if comando == "listar_remota":
                listar_remote(conn, ruta_remota_actual)
            elif comando.startswith("crear_remota:"):
                nueva_carpeta = comando.split(":")[1]
                crear_remote(conn, ruta_remota_actual, nueva_carpeta)
            elif comando.startswith("eliminar_remota:"):
                item = comando.split(":")[1]
                eliminar_remote(conn, ruta_remota_actual, item)
            elif comando.startswith("cambiar_directorio_remota:"):
                # Verificar si el comando recibido comienza con "cambiar_directorio_remota:"
                ruta_relativa = comando.split(":")[1]
                # Obtener la ruta relativa proporcionada en el comando
                nueva_ruta = os.path.join(ruta_remota_actual, ruta_relativa)
                # Combinar la ruta remota actual con la ruta relativa para obtener la nueva ruta completa
                print("Ruta1:", nueva_ruta) 
                nueva_ruta = os.path.normpath(nueva_ruta)  # Normalizar la ruta
                print("Ruta2:", nueva_ruta)  
                # Normalizar la nueva ruta para asegurarse de que esté en un formato válido
                if os.path.isdir(nueva_ruta):
                    # Verificar si la nueva ruta es un directorio existente
                    ruta_remota_actual = nueva_ruta
                    # Actualizar la ruta remota actual con la nueva ruta
                    listar_remote(conn, ruta_remota_actual)
                    # Enviar al cliente la lista actualizada de archivos y carpetas en la nueva ruta remota
                else:
                    conn.sendall(b"La carpeta no existe.")
                    # Enviar al cliente un mensaje indicando que la carpeta no existe

            elif comando.startswith("regresar_directorio_remota"):
                ruta_relativa = comando.split(":")[1] #Obtenemos la ruta relativa ej: /carpeta1/carpeta2
                print("Ruta Relativa:", ruta_relativa)
                nueva_ruta = os.path.join(ruta_remota_actual, ruta_relativa)
                print("Nueva Ruta:", nueva_ruta)
                if ruta_remota_actual == ruta_remota:
                    conn.sendall("Ya estas en la carpeta Raiz.".encode('utf-8'))
                else:
                    ruta_remota_actual = os.path.dirname(ruta_remota_actual)
                    listar_remote(conn, ruta_remota_actual)
            elif comando.startswith("enviar_archivo"):
                nombre_archivo = comando.split(":")[1]
                ruta_archivo = os.path.join(ruta_remota_actual, nombre_archivo)
                with open(ruta_archivo, "wb") as f:
                    while True:
                        data = conn.recv(4096)
                        if b"fin_archivo" in data:
                            # Encuentra la posición de "fin_archivo" en los datos
                            fin_pos = data.index(b"fin_archivo")
                            # Escribe solo los datos que preceden a "fin_archivo" en el archivo
                            f.write(data[:fin_pos])
                            break # Sale del bucle
                        else:
                            f.write(data)

    except ConnectionResetError:
        print(f"Conexión reiniciada por el cliente {addr}")
    finally:
        conn.close()