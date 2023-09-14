# Compresor de imágenes
# Creado por: LeoValdi
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor

def comprimir_imagen(nombre, carpeta):
    name, extension = os.path.splitext(carpeta + nombre)
    if extension in [".jpg",".JPG",".JPEG", ".jpeg"]:
        print(f"Comprimiendo {nombre}...")
        img = Image.open(carpeta + '\\' + nombre)


        #Hacer que todas las imagenes tengan el mismo tamaño
        if img.width > img.height:
            horizontal = True
            width = int(1300)
            height = int(width * img.height / img.width)
        else:
            height = int(1300)
            width = int(height * img.width / img.height)
            horizontal = False

        print('Imagen original: ', img.size)
        # Define los límites de tamaño (puedes ajustar estos valores según tus necesidades)
        #limite_1 = 6000 * 6000  # Por ejemplo, primer límite de 36 millones de píxeles
        #limite_2 = 5000 * 3000  # Por ejemplo, segundo límite de 9 millones de píxeles

        # Calcula el tamaño de la imagen original en píxeles
        tamaño_original = img.width * img.height

        # Calcula el factor de escala en base al tamaño de la imagen original

        #if tamaño_original >= limite_1:
        #    porcentaje_de_escala = 25 / 100.0
        #elif tamaño_original >= limite_2:
        #    porcentaje_de_escala = 45 / 100.0
        #else:
        #    porcentaje_de_escala = 60 / 100.0

        # Calculate the new dimensions
        #width = int(img.width * porcentaje_de_escala)
        #height = int(img.height * porcentaje_de_escala)

        # Resize the image
        print("Redimensionando...")
        resized = img.resize((width, height), Image.ANTIALIAS)

        print('Imagen redimensionada: ', resized.size)

        # Save the resized image
        nombre_carpeta = f'{carpeta}/comprimir'
        if not os.path.exists(nombre_carpeta):
            os.makedirs(nombre_carpeta)

        guardar = f'{nombre_carpeta}/{nombre.split(".")[0]}_comp.jpg'
        #guardar = f'{nombre_carpeta}/{nombre.split(".")[0]}_horizontal {horizontal}.jpg'
        resized.save(guardar,
                     optimize=True, quality=40, icc_profile=resized.info.get('icc_profile'))
        

        print('Imagen guardada en: ', guardar)


# Load the image
root = tk.Tk()
root.withdraw()

# Use askdirectory() instead of askopenfilename()
carpeta = filedialog.askdirectory()

print(f'Ruta: {carpeta}')

# Number of cores (you can adjust this according to your machine's capabilities)
num_cores = 4

# List all the image files in the folder
imagenes = [nombre for nombre in os.listdir(carpeta) if os.path.splitext(nombre)[1] in [".jpg",".JPG",".JPEG", ".jpeg"]]

with ThreadPoolExecutor(max_workers=num_cores) as executor:
    executor.map(comprimir_imagen, imagenes, [carpeta]*len(imagenes))

input("Presiona ENTER para salir...")