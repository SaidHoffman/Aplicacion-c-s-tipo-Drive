import socket
import os
import shutil
import zipfile
import json

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

def obtener_tamaño(ruta):
    if os.path.isfile(ruta):
        # Si es un archivo, devolver su tamaño
        return os.path.getsize(ruta)
    else:
        # Si es un directorio, sumar el tamaño de todos los archivos que contiene
        return sum(obtener_tamaño(os.path.join(ruta, nombre)) for nombre in os.listdir(ruta))

def listar_remote(conn, ruta_remota):
    """
    Envía al cliente una tupla de los archivos y carpetas en la ruta remota actual con su nombre, tipo y tamaño.

    Args:
        conn (socket.socket): El socket de la conexión con el cliente.
        ruta_remota (str): La ruta remota actual.
    """

    contenido = os.listdir(ruta_remota)
    print("Contenido:", contenido)
    if not contenido:
        conn.sendall("La carpeta está vacía.".encode('utf-8'))
    else:
        lista_item = []
        for item in contenido:
            ruta_item = os.path.join(ruta_remota, item)
            tipo = "Carpeta" if os.path.isdir(ruta_item) else "Archivo"
            tamaño = obtener_tamaño(ruta_item)
            lista_item.append((item, tipo, tamaño))
        # Convertir la lista en una cadena JSON
        lista_item_json = json.dumps(lista_item)

        # Enviar la cadena JSON a través del socket
        conn.sendall(lista_item_json.encode('utf-8'))

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
        conn.sendall(b"Carpeta creada.")
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
            conn.sendall(b"Carpeta eliminada.")
        except OSError as e:
            conn.sendall(bytes(f"No se pudo eliminar la carpeta: {e.strerror}", encoding='utf-8'))
    else:
        try:
            os.remove(ruta_item)
            conn.sendall(b"Archivo eliminado.")
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
                    # Enviar al cliente la confirmacion
                    conn.sendall(bytes(ruta_remota_actual, encoding='utf-8'))
                else:
                    conn.sendall(b"ERROR.")
                    # Enviar al cliente un mensaje indicando que la carpeta no existe

            elif comando.startswith("regresar_directorio_remota"):

                if ruta_remota_actual == ruta_remota:
                    conn.sendall(b"ERROR.")
                else:
                    # Obtener la ruta base de la ruta remota actual
                    ruta_base = os.path.dirname(ruta_remota_actual)
                    # Actualizar la ruta remota actual
                    ruta_remota_actual = ruta_base
                    # Enviar al cliente la nueva ruta remota actual
                    conn.sendall(bytes(ruta_remota_actual, encoding='utf-8'))
                
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
                conn.sendall(b"Archivo recibido.")
            elif comando.startswith("enviar_carpeta"):
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
                            break
                        else:
                            f.write(data)

                # Obtener el nombre base del archivo (sin la extensión .zip)
                nombre_base = os.path.splitext(os.path.basename(ruta_archivo))[0]
                # Crear una nueva carpeta con el nombre base del archivo
                nueva_carpeta = os.path.join(ruta_remota_actual, nombre_base)
                os.mkdir(nueva_carpeta)

                # Extraer el archivo zip en la nueva carpeta
                with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
                    zip_ref.extractall(nueva_carpeta)
                #Eliminar el archivo zip
                os.remove(ruta_archivo)
                conn.sendall(b"Carpeta recibida.")
            
            elif comando.startswith("solicitar_archivo"):
                nombre_archivo = comando.split(":")[1]
                ruta_archivo = os.path.join(ruta_remota_actual, nombre_archivo)
                if not os.path.isdir(ruta_archivo):
                    conn.sendall(b"archivo")
                    with open(ruta_archivo, "rb") as f:
                        while True:
                            data = f.read(4096)
                            if not data:
                                break
                            conn.sendall(data)
                    conn.sendall(b"fin_archivo")
                else:
                    # Comprimir la carpeta en un archivo zip
                    conn.sendall(b"carpeta")
                    with zipfile.ZipFile(f"{ruta_archivo}.zip", 'w') as zip_ref:
                        for carpeta, _, archivos in os.walk(ruta_archivo):
                            for archivo in archivos:
                                ruta_completa = os.path.join(carpeta, archivo)
                                ruta_relativa = os.path.relpath(ruta_completa, ruta_archivo)
                                zip_ref.write(ruta_completa, ruta_relativa)
                    # Enviar el archivo zip al cliente
                    with open(f"{ruta_archivo}.zip", "rb") as f:
                        while True:
                            data = f.read(4096)
                            if not data:
                                break
                            conn.sendall(data)
                    conn.sendall(b"fin_archivo")
                    # Eliminar el archivo zip
                    os.remove(f"{ruta_archivo}.zip")

    except ConnectionResetError:
        print(f"Conexión reiniciada por el cliente {addr}")
    finally:
        conn.close()