import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, messagebox
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def comprimir_imagen(nombre, carpeta):
    try:
        name, extension = os.path.splitext(carpeta + nombre)
        if extension in [".jpg",".JPG",".JPEG", ".jpeg"]:
            print(f"Comprimiendo {nombre}...")
            img = Image.open(carpeta + '//' + nombre)

            # Making all images have the same size
            if img.width > img.height:
                horizontal = True
                width = int(1950)
                height = int(width * img.height / img.width)
            else:
                height = int(1950)
                width = int(height * img.width / img.height)
                horizontal = False

            print('Imagen original:', img.size)

            # Resize the image
            resized = img.resize((width, height), Image.ANTIALIAS)
            print('Imagen redimensionada:', resized.size)

            # Save the resized image
            nombre_carpeta = f'{carpeta}/comprimir'
            if not os.path.exists(nombre_carpeta):
                os.makedirs(nombre_carpeta)

            guardar = f'{nombre_carpeta}/{nombre.split(".")[0]}_comp.jpg'
            resized.save(guardar,
                         optimize=True, quality=50, icc_profile=resized.info.get('icc_profile'))
            print('Imagen guardada en:', guardar)
    except Exception as e:
        print(f"Error al procesar {nombre} en {carpeta}: {str(e)}")

def on_drop(event):
    print(f"Raw data from event: {event.data}")  # Imprimir la data cruda
    carpeta = event.data.replace("{", "").replace("}", "").strip()  # Eliminar las llaves y espacios adicionales
    if os.path.isdir(carpeta) and carpeta not in carpetas:
        print(f"Carpeta añadida: {carpeta}")
        listbox.insert(tk.END, carpeta)
        carpetas.append(carpeta)
    else:
        print(f"Error añadiendo: {carpeta}. ¿Es una carpeta válida?")

def start_processing():
    try:
        num_cores = 12
        for carpeta in carpetas:
            print(f'Ruta: {carpeta}')
            imagenes = [nombre for nombre in os.listdir(carpeta) if os.path.splitext(nombre)[1] in [".jpg",".JPG",".JPEG", ".jpeg"]]
            with ThreadPoolExecutor(max_workers=num_cores) as executor:
                executor.map(comprimir_imagen, imagenes, [carpeta]*len(imagenes))
        print("Procesamiento completado!")
    except Exception as e:
        print(f"Error general: {str(e)}")

root = TkinterDnD.Tk()
root.title('Arrastra y suelta las carpetas a procesar')

listbox = tk.Listbox(root, width=50, height=10)
listbox.pack(padx=10, pady=10)

btn_start = tk.Button(root, text="Comenzar procesamiento", command=start_processing)
btn_start.pack(pady=20)

carpetas = []

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
