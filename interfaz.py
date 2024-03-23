import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def obtener_tamaño(ruta):
    if os.path.isfile(ruta):
        # Si es un archivo, devolver su tamaño
        return os.path.getsize(ruta)
    else:
        # Si es un directorio, sumar el tamaño de todos los archivos que contiene
        return sum(obtener_tamaño(os.path.join(ruta, nombre)) for nombre in os.listdir(ruta))

root = tk.Tk()
root.title("Administrador de archivos")

# Crear un Frame para contener los widgets
frame_local = tk.Frame(root)
frame_local.pack(side=tk.LEFT, padx=10, pady=10)

# Crear el encabezado
encabezado = tk.Frame(frame_local) # Crea un nuevo frame para el encabezado
encabezado.pack(side=tk.TOP, fill=tk.X) # Agrega el encabezado al frame local

# Crear la etiqueta de título
titulo = tk.Label(encabezado, text="Archivos Locales", font=("Helvetica", 14, "bold"))
titulo.pack(side=tk.LEFT, padx=5, pady=5) # Agrega la etiqueta al encabezado

# Crear el botón para refrescar
icono_refrescar = tk.PhotoImage(file="assets/arrows-rotate-solid.png") 
icono_refrescar = icono_refrescar.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_refrescar = tk.Button(encabezado, image=icono_refrescar)
btn_refrescar.pack(side=tk.LEFT, padx=10, pady=5)

# Crear el botón para crear una carpeta
icono_crear = tk.PhotoImage(file="assets/folder-plus-solid.png") 
icono_crear = icono_crear.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_crear = tk.Button(encabezado, image=icono_crear)
btn_crear.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el botón para eliminar
icono_eliminar = tk.PhotoImage(file="assets/trash-solid.png") 
icono_eliminar = icono_eliminar.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_eliminar = tk.Button(encabezado, image=icono_eliminar)
btn_eliminar.pack(side=tk.LEFT, padx=5, pady=5)

# Crear el botón para enviar
icono_enviar = tk.PhotoImage(file="assets/paper-plane-regular.png") 
icono_enviar = icono_enviar.subsample(16, 16)  # Reducir el tamaño de la imagen a la mitad
btn_enviar = tk.Button(encabezado, image=icono_enviar)
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
treeview = ttk.Treeview(frame_lista_local)
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


root.mainloop()