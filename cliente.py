import socket # Importa el módulo socket para la comunicación en red
import os # Importa el módulo os para interactuar con el sistema operativo
import shutil # Importa el módulo shutil para operaciones de archivos y directorios
import tkinter as tk # Importa el módulo tkinter para crear la interfaz gráfica
import zipfile # Importa el módulo zipfile para comprimir y descomprimir archivos
from tkinter import filedialog, messagebox, simpledialog # Importa los módulos específicos de tkinter
from tkinter import ttk # Importa el módulo ttk de tkinter para widgets mejorados
import json

# Leer las rutas de carpetas desde el archivo "rutas.txt"
with open("rutas.txt", "r") as f:
    rutas = f.read().splitlines() # Lee las rutas de las carpetas local y remota desde el archivo "rutas.txt"
    ruta_local = rutas[0] # Asigna la primera línea del archivo a la ruta de la carpeta local
    ruta_remota = rutas[1] # Asigna la segunda línea del archivo a la ruta de la carpeta remota

# Crear el socket del cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crea un socket TCP/IP
client_socket.connect(('localhost', 1234)) # Se conecta al servidor en localhost:1234
print("Conectado al servidor.") # Imprime un mensaje indicando la conexión exitosa

# Variables para almacenar las rutas de carpetas actuales
ruta_local_actual = ruta_local # Inicializa la ruta de la carpeta local actual
ruta_remota_actual = ruta_remota # Inicializa la ruta de la carpeta remota actual

# Funciones para las operaciones de archivos y carpetas
def listar_local():
    global ruta_local_actual
    contenido = os.listdir(ruta_local_actual) # Obtiene una lista de archivos y carpetas en la ruta local actual
    treeview.delete(*treeview.get_children()) # Limpia el Treeview de la interfaz gráfica

    for item in contenido: # Itera sobre los elementos de la lista
        ruta_item = os.path.join(ruta_local_actual, item) # Construye la ruta completa del elemento
        if os.path.isdir(ruta_item): # Si el elemento es una carpeta
            treeview.insert("", tk.END, image=icono_carpeta, values=(item, "")) # Agrega la carpeta al Treeview con un icono de carpeta
        else: # Si el elemento es un archivo
            treeview.insert("", tk.END, image=icono_archivo, values=(item, str(obtener_tamaño(ruta_item)) + " bytes")) # Agrega el archivo al Treeview con un icono de archivo

def listar_remota():
    global ruta_remota_actual
    client_socket.sendall(b"listar_remota") # Envía el comando "listar_remota" al servidor
    data = client_socket.recv(4096) # Recibe la respuesta del servidor

    treeview_remota.delete(*treeview_remota.get_children()) # Limpia el Treeview de la interfaz gráfica

    try: # Intenta decodificar la cadena de bytes a una cadena de texto y luego convertirla en una lista
        # Decodificar la cadena de bytes a una cadena de texto y luego convertirla en una lista
        data = json.loads(data.decode('utf-8'))

        for item in data: # Itera sobre los elementos de la respuesta
            if item[1] == "Carpeta": # Si el elemento es una carpeta
                treeview_remota.insert("", tk.END, image=icono_carpeta, values=(item[0], ""))
            else: # Si el elemento es un archivo
                treeview_remota.insert("", tk.END, image=icono_archivo, values=(item[0], str(item[2]) + " bytes"))
    except json.JSONDecodeError:
        # Si la conversión falla, asume que la respuesta es "La carpeta está vacía" y agrega ese mensaje al Treeview
        treeview_remota.insert("", tk.END, values=("La carpeta está vacía", ""))

def crear_local():
    global ruta_local_actual
    nueva_carpeta = simpledialog.askstring("Nueva Carpeta", "Ingrese el nombre de la nueva carpeta:") # Muestra un cuadro de diálogo para ingresar el nombre de la nueva carpeta
    if nueva_carpeta: # Si se ingresó un nombre válido
        nueva_ruta = os.path.join(ruta_local_actual, nueva_carpeta) # Construye la ruta completa de la nueva carpeta
        if os.path.exists(nueva_ruta): # Si la carpeta ya existe
            messagebox.showerror("Error", "La carpeta ya existe.") # Muestra un mensaje de error
        else:
            try:
                os.makedirs(nueva_ruta) # Crea la nueva carpeta
                listar_local() # Actualiza la lista de archivos y carpetas en la interfaz gráfica
            except OSError as e:
                messagebox.showerror("Error", f"No se pudo crear la carpeta: {e.strerror}") # Muestra un mensaje de error si ocurrió un problema al crear la carpeta

def eliminar_local():
    global ruta_local_actual
    seleccionado = treeview.selection() # Obtiene el índice del elemento seleccionado en el Treeview
    if seleccionado: # Si hay elementos seleccionados
        confirmacion = messagebox.askyesno("Confirmación", f"Se van a eliminar {len(seleccionado)} archivos.\n¿Desea continuar?") # Muestra un mensaje de confirmación

        if confirmacion: # Si el usuario hizo clic en "Sí"
            for item in seleccionado: # Itera sobre los elementos seleccionados
                nombre = treeview.item(item, "values")[0] # Obtiene el nombre del elemento seleccionado
                ruta_item = os.path.join(ruta_local_actual, nombre) # Construye la ruta completa del elemento
                if os.path.isdir(ruta_item): # Si el elemento es una carpeta
                    try:
                        shutil.rmtree(ruta_item) # Elimina la carpeta
                    except OSError as e:
                        messagebox.showerror("Error", f"No se pudo eliminar la carpeta: {e.strerror}")
                else: # Si el elemento es un archivo
                    try:
                        os.remove(ruta_item) # Elimina el archivo
                    except OSError as e:
                        messagebox.showerror("Error", f"No se pudo eliminar el archivo: {e.strerror}")
            listar_local() # Actualiza la lista de archivos y carpetas en la interfaz gráfica
    else:
        messagebox.showerror("Error", "No se ha seleccionado ningún archivo.") # Muestra un mensaje de error si no hay elementos seleccionados

            

def crear_remota():
    nueva_carpeta = simpledialog.askstring("Nueva Carpeta", "Ingrese el nombre de la nueva carpeta:") # Muestra un cuadro de diálogo para ingresar el nombre de la nueva carpeta
    if nueva_carpeta: # Si se ingresó un nombre válido
        client_socket.sendall(bytes(f"crear_remota:{nueva_carpeta}", encoding='utf-8')) # Envía el comando "crear_remota" y el nombre de la nueva carpeta al servidor
        respuesta = client_socket.recv(1024).decode('utf-8') # Recibe la respuesta del servidor
        if respuesta.startswith("La carpeta ya existe."): # Si la respuesta contiene un mensaje de error
            messagebox.showerror("Error", "No se pudo crear la carpeta, verifique su nombre ingresado") # Muestra el mensaje de error
        listar_remota() # Actualiza la lista de archivos y carpetas en la interfaz gráfica


def eliminar_remota():
    seleccionado = treeview_remota.selection() # Obtiene el índice del elemento seleccionado en el Treeview
    if seleccionado: # Si hay elementos seleccionados
        confirmacion = messagebox.askyesno("Confirmación", f"Se van a eliminar {len(seleccionado)} archivos.\n¿Desea continuar?") # Muestra un mensaje de confirmación
        if confirmacion: # Si el usuario hizo clic en "Sí"
            for item in seleccionado: # Itera sobre los elementos seleccionados
                nombre = treeview_remota.item(item, "values")[0] # Obtiene el nombre del elemento seleccionado
                client_socket.sendall(bytes(f"eliminar_remota:{nombre}", encoding='utf-8')) # Envía el comando "eliminar_remota" y el nombre del elemento al servidor

                # Espera a recibir la confirmación del servidor
                data = client_socket.recv(1024)
                print(f"Respuesta del servidor: {data.decode('utf-8')}")

            listar_remota() # Actualiza la lista de archivos y carpetas en la interfaz gráfica

def cambiar_directorio_remota(nombre):
    global ruta_remota_actual
    client_socket.sendall(bytes(f"cambiar_directorio_remota:{nombre}", encoding='utf-8')) # Envía el comando "cambiar_directorio_remota" y el nombre de la carpeta al servidor
    data = client_socket.recv(4096) # Recibe la respuesta del servidor
    if data.startswith(b"ERROR"):
        messagebox.showerror("Error", "No se pudo cambiar de directorio.")
    else:
        listar_remota()

def regresar_directorio_remota():
    global ruta_remota_actual
    client_socket.sendall(bytes(f"regresar_directorio_remota", encoding='utf-8')) # Envía el comando "regresar_directorio_remota" y la ruta relativa al servidor
    data = client_socket.recv(4096) # Recibe la respuesta del servidor
    if data.startswith(b"ERROR"):
        messagebox.showerror("Error", "Ya estas en la carpeta raiz.")
    else:
        ruta_remota_actual = data.decode('utf-8') # Actualiza la ruta de la carpeta remota actual
        listar_remota()

def cambiar_directorio_local(nombre):
    global ruta_local_actual
    #Comprobar si el archivo seleccionado es una carpeta
    try:
        nueva_ruta = os.path.join(ruta_local_actual, nombre) # Construye la ruta completa del nuevo directorio
        nueva_ruta = os.path.normpath(nueva_ruta) # Normalizar la ruta
        if os.path.isdir(nueva_ruta): # Si el elemento es una carpeta
            ruta_local_actual = nueva_ruta # Actualiza la ruta de la carpeta local actual
            listar_local() # Actualiza la lista de archivos y carpetas en la interfaz gráfica
        else:
            messagebox.showerror("Error", "No es un directorio válido.") # Muestra un mensaje de error si el elemento seleccionado no es una carpeta válida
    except Exception:
        messagebox.showerror("Error", "No se pudo cambiar de directorio.") # Muestra un mensaje de error si ocurrió un problema al cambiar de directorio

def regresar_directorio_local():
    global ruta_local_actual
    if ruta_local_actual != ruta_local: # Si la carpeta actual no es la carpeta raíz
        ruta_local_actual = os.path.dirname(ruta_local_actual) # Actualiza la ruta de la carpeta local actual al directorio padre
        listar_local() # Actualiza la lista de archivos y carpetas en la interfaz gráfica
    else:
        messagebox.showerror("Error", "Ya estás en la carpeta raíz.") # Muestra un mensaje de error si ya está en la carpeta raíz

def enviar_archivo():
    seleccionados = treeview.selection() # Obtiene los índices de los elementos seleccionados en el Treeview
    if seleccionados: # Si hay elementos seleccionados
        confirmacion = messagebox.askyesno("Confirmación", f"Se van a enviar {len(seleccionados)} archivos al servidor.\n¿Desea continuar?") # Muestra un mensaje de confirmación
        if confirmacion: # Si el usuario hizo clic en "Sí"
            for item in seleccionados: # Itera sobre los elementos seleccionados
                nombre = treeview.item(item, "values")[0] # Obtiene el nombre del elemento seleccionado
                ruta_archivo = os.path.join(ruta_local_actual, nombre)
                if os.path.isdir(ruta_archivo): # Si el elemento es una carpeta
                    with zipfile.ZipFile(f"{nombre}.zip", "w") as zipf:
                        for raiz, directorios, archivos in os.walk(ruta_archivo):
                            for archivo in archivos:
                                zipf.write(os.path.join(raiz, archivo), os.path.relpath(os.path.join(raiz, archivo), ruta_archivo)) # Agrega cada archivo al archivo ZIP
                    
                    #Enviar el archivo ZIP al servidor
                    with open(f"{nombre}.zip", "rb") as f:
                        client_socket.sendall(bytes(f"enviar_carpeta:{nombre}.zip", encoding='utf-8'))
                        while True:
                            data = f.read(4096)
                            if not data:
                                break
                            client_socket.sendall(data)

                    client_socket.sendall(bytes("fin_archivo", encoding='utf-8')) # Envía un comando para indicar el fin del archivo
                    os.remove(f"{nombre}.zip") # Elimina el archivo ZIP después de enviarlo
                    respuesta = client_socket.recv(1024).decode('utf-8')

                else: # Si el elemento es un archivo
                    client_socket.sendall(bytes(f"enviar_archivo:{nombre}", encoding='utf-8')) # Envía el comando "enviar_archivo" y el nombre del archivo al servidor
                    with open(ruta_archivo, "rb") as f: # Abre el archivo en modo binario
                        while True: # Bucle para enviar el archivo en bloques
                            data = f.read(4096) # Lee un bloque de datos del archivo
                            if not data: # Si no hay más datos
                                break # Sale del bucle
                            client_socket.sendall(data) # Envía el bloque de datos al servidor
                    client_socket.sendall(bytes("fin_archivo", encoding='utf-8')) # Envía un comando para indicar el fin del archivo
                    respuesta = client_socket.recv(1024).decode('utf-8') # Recibe la respuesta del servidor

        listar_remota() # Actualiza la lista de archivos y carpetas en la interfaz gráfica
        messagebox.showinfo("Información", "Los archivos se han enviado correctamente.") # Muestra un mensaje de información

def solicitar_archivo():
    seleccionados = treeview_remota.selection() # Obtiene los índices de los elementos seleccionados en el Treeview
    if seleccionados: # Si hay elementos seleccionados
        confirmacion = messagebox.askyesno("Confirmación", f"Se van a descargar {len(seleccionados)} archivos desde el servidor.\n¿Desea continuar?") # Muestra un mensaje de confirmación
        if confirmacion: # Si el usuario hizo clic en "Sí"
            for item in seleccionados: # Itera sobre los elementos seleccionados
                nombre = treeview_remota.item(item, "values")[0] # Obtiene el nombre del elemento seleccionado
                client_socket.sendall(bytes(f"solicitar_archivo:{nombre}", encoding='utf-8')) # Envía el comando "solicitar_archivo" y el nombre del archivo al servidor
                tipo = client_socket.recv(1024).decode('utf-8') # Recibe el tipo del archivo (Carpeta o Archivo)
                if tipo.startswith("carpeta"):
                    ruta_archivo = os.path.join(ruta_local_actual, nombre + ".zip") # Construye la ruta completa del archivo a descargar
                else:
                    ruta_archivo = os.path.join(ruta_local_actual, nombre)

                with open(ruta_archivo, "wb") as f: # Abre el archivo en modo binario
                    while True: # Bucle para recibir el archivo en bloques
                        data = client_socket.recv(4096) # Recibe un bloque de datos del servidor
                        if b"fin_archivo" in data: # Si se recibe el comando para indicar el fin del archivo
                            f.write(data.replace(b"fin_archivo", b"")) # Escribe los datos en el archivo sin el comando de fin
                            break # Sale del bucle
                        f.write(data) # Escribe los datos en el archivo
                try:
                    # Comprueba si el archivo es un archivo ZIP
                    if ruta_archivo.endswith('.zip'):
                        # Obtén el nombre del archivo sin la extensión .zip
                        nombre_carpeta = os.path.splitext(os.path.basename(ruta_archivo))[0]

                        # Crea la ruta de la nueva carpeta
                        ruta_carpeta = os.path.join(os.path.dirname(ruta_archivo), nombre_carpeta)

                        # Crea la nueva carpeta si no existe
                        os.makedirs(ruta_carpeta, exist_ok=True)

                        with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
                            # Extrae el contenido del archivo ZIP en la nueva carpeta
                            zip_ref.extractall(ruta_carpeta)

                        os.remove(ruta_archivo)
                except zipfile.BadZipFile:
                    pass

                messagebox.showinfo("Información", "Los archivos se han recibido correctamente.") # Muestra un mensaje de información
                listar_local() # Actualiza la lista de archivos y carpetas en la interfaz gráfica
    else:
        messagebox.showerror("Error", "No se ha seleccionado ningún archivo.") # Muestra un mensaje de error si no hay elementos seleccionados

def salir_aplicacion():
    client_socket.close() # Cierra el socket del cliente
    root.quit() # Cierra la ventana de la interfaz gráfica

# Función para obtener el tamaño de un archivo o directorio
def obtener_tamaño(ruta):
    if os.path.isfile(ruta):
        # Si es un archivo, devolver su tamaño
        return os.path.getsize(ruta)
    else:
        # Si es un directorio, sumar el tamaño de todos los archivos que contiene
        return sum(obtener_tamaño(os.path.join(ruta, nombre)) for nombre in os.listdir(ruta))
    
def on_doble_click(event):
    # Obtener el elemento seleccionado
    seleccionado = treeview.selection()

    if seleccionado:
        # Si hay un elemento seleccionado, obtener sus valores
        valores = treeview.item(seleccionado[0], "values")
        nombre = valores[0]  # Suponiendo que el nombre es el primer valor

        # Llamar a la función cambiar_directorio_local con el nombre del elemento seleccionado
        cambiar_directorio_local(nombre)

def on_doble_click2(event):
    # Obtener el elemento seleccionado
    seleccionado = treeview_remota.selection()

    if seleccionado:
        # Si hay un elemento seleccionado, obtener sus valores
        valores = treeview_remota.item(seleccionado[0], "values")
        nombre = valores[0]  # Suponiendo que el nombre es el primer valor

        # Llamar a la función cambiar_directorio_local con el nombre del elemento seleccionado
        cambiar_directorio_remota(nombre)
    
# Interfaz gráfica
root = tk.Tk() # Crea la ventana principal de la interfaz gráfica
root.title("Administrador de Archivos") # Establece el título de la ventana

# Crear un Frame para contener los widgets
frame_local = tk.Frame(root)
frame_local.pack(side=tk.LEFT, padx=10, pady=10)

# Crear el encabezado
encabezado = tk.Frame(frame_local) # Crea un nuevo frame para el encabezado
encabezado.pack(side=tk.TOP, fill=tk.X) # Agrega el encabezado al frame local

# Crear la etiqueta de título
titulo = tk.Label(encabezado, text="Archivos Locales", font=("Helvetica", 14, "bold"))
titulo.pack(side=tk.LEFT, padx=5, pady=5) # Agrega la etiqueta al encabezado

# Crear el botón para regresar
icono_regresar = tk.PhotoImage(file="assets/arrow-up-solid.png") 
icono_regresar = icono_regresar.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_regresar = tk.Button(encabezado, image=icono_regresar, command=regresar_directorio_local)
btn_regresar.pack(side=tk.LEFT, padx=[10,5], pady=5)

# Crear el botón para refrescar
icono_refrescar = tk.PhotoImage(file="assets/arrows-rotate-solid.png") 
icono_refrescar = icono_refrescar.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_refrescar = tk.Button(encabezado, image=icono_refrescar, command=listar_local)
btn_refrescar.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el botón para crear una carpeta
icono_crear = tk.PhotoImage(file="assets/folder-plus-solid.png") 
icono_crear = icono_crear.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_crear = tk.Button(encabezado, image=icono_crear, command=crear_local)
btn_crear.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el botón para eliminar
icono_eliminar = tk.PhotoImage(file="assets/trash-solid.png") 
icono_eliminar = icono_eliminar.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_eliminar = tk.Button(encabezado, image=icono_eliminar, command=eliminar_local)
btn_eliminar.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el botón para enviar
icono_enviar = tk.PhotoImage(file="assets/paper-plane-regular.png") 
icono_enviar = icono_enviar.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_enviar = tk.Button(encabezado, image=icono_enviar, command=enviar_archivo)
btn_enviar.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el Frame para la lista de archivos locales
frame_lista_local = tk.Frame(frame_local)
frame_lista_local.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Cargar las imágenes para los iconos de carpeta y archivo
icono_carpeta = tk.PhotoImage(file="assets/folder-regular.png")
icono_carpeta = icono_carpeta.subsample(32, 32)  # Reducir el tamaño de la imagen a la mitad
icono_archivo = tk.PhotoImage(file="assets/file-regular.png")
icono_archivo = icono_archivo.subsample(32, 32)  # Reducir el tamaño de la imagen a la mitad

# Crear el Treeview
treeview = ttk.Treeview(frame_lista_local, selectmode=tk.EXTENDED)
treeview.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

# Agregar las columnas al Treeview
treeview["columns"] = ("Nombre", "Tamaño")

# Configurar las columnas
treeview.column("#0", anchor=tk.W, width=40, stretch=tk.NO)
treeview.column("Nombre", anchor=tk.W, width=120)
treeview.column("Tamaño", anchor=tk.W, width=80)

# Configurar los encabezados de las columnas
treeview.heading("#0", text="", anchor=tk.W)
treeview.heading("Nombre", text="Nombre", anchor=tk.W)
treeview.heading("Tamaño", text="Tamaño", anchor=tk.W)

# Vincular el evento de doble clic con la función on_doble_click
treeview.bind("<Double-1>", on_doble_click)

# Frame para la carpeta remota
# Crear un Frame para contener los widgets
frame_remota = tk.Frame(root)
frame_remota.pack(side=tk.RIGHT, padx=10, pady=10)

# Crear el encabezado
encabezado_remota = tk.Frame(frame_remota) # Crea un nuevo frame para el encabezado
encabezado_remota.pack(side=tk.TOP, fill=tk.X) # Agrega el encabezado al frame remota

# Crear la etiqueta de título
titulo_remota = tk.Label(encabezado_remota, text="Archivos Remotos", font=("Helvetica", 14, "bold"))
titulo_remota.pack(side=tk.LEFT, padx=5, pady=5) # Agrega la etiqueta al encabezado

# Crear el botón para regresar
btn_regresar_remota = tk.Button(encabezado_remota, image=icono_regresar, command=regresar_directorio_remota)
btn_regresar_remota.pack(side=tk.LEFT, padx=[10,5], pady=5)

# Crear el botón para refrescar
btn_refrescar_remota = tk.Button(encabezado_remota, image=icono_refrescar, command=listar_remota)
btn_refrescar_remota.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el botón para crear una carpeta
btn_crear_remota = tk.Button(encabezado_remota, image=icono_crear, command=crear_remota)
btn_crear_remota.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el botón para eliminar
btn_eliminar_remota = tk.Button(encabezado_remota, image=icono_eliminar, command=eliminar_remota)
btn_eliminar_remota.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el botón para solicitar
icono_solicitar = tk.PhotoImage(file="assets/download-solid.png") 
icono_solicitar = icono_solicitar.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_solicitar = tk.Button(encabezado_remota, image=icono_solicitar, command=solicitar_archivo)
btn_solicitar.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el Frame para la lista de archivos remotos
frame_lista_remota = tk.Frame(frame_remota)
frame_lista_remota.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Crear el Treeview
treeview_remota = ttk.Treeview(frame_lista_remota, selectmode=tk.EXTENDED)
treeview_remota.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

# Agregar las columnas al Treeview
treeview_remota["columns"] = ("Nombre", "Tamaño")

# Configurar las columnas
treeview_remota.column("#0", anchor=tk.W, width=40, stretch=tk.NO)
treeview_remota.column("Nombre", anchor=tk.W, width=120)
treeview_remota.column("Tamaño", anchor=tk.W, width=80)

# Configurar los encabezados de las columnas
treeview_remota.heading("#0", text="", anchor=tk.W)
treeview_remota.heading("Nombre", text="Nombre", anchor=tk.W)
treeview_remota.heading("Tamaño", text="Tamaño", anchor=tk.W)

# Vincular el evento de doble clic con la función on_doble_click
treeview_remota.bind("<Double-1>", on_doble_click2)

btn_salir = tk.Button(root, text="Salir", command=salir_aplicacion)
btn_salir.pack(side=tk.BOTTOM, pady=10)

# Inicializar las listas de carpetas
listar_local()
listar_remota()

# Iniciar el bucle principal de la interfaz gráfica
root.mainloop() 