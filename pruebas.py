from concurrent.futures import as_completed
import os
from PIL import Image, JpegImagePlugin
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
import webbrowser
import threading


def comprimir_imagen(ruta, selected_folder, quality, resize_option, width_or_percentage, height=None, cancel_event=None):

    # Agregar una verificación para cancelar el proceso
    if cancel_event and cancel_event.is_set():
        return

    """Función para comprimir una imagen usando la funcionalidad de PIL."""
    imagen_original = Image.open(ruta)
    formato = imagen_original.format
    if formato != 'JPEG':
        raise ValueError("El formato de imagen no es JPEG")

    # Redimensionar la imagen según la opción seleccionada
    if resize_option == "percentage":
        new_width = int(imagen_original.width * width_or_percentage)
        new_height = int(imagen_original.height * width_or_percentage)
    else:
        new_width = width_or_percentage
        new_height = height

    imagen_redimensionada = imagen_original.resize(
        (new_width, new_height), Image.LANCZOS)
    nombre, ext = os.path.splitext(os.path.basename(ruta))

    output_folder = os.path.join(selected_folder, 'comprimido')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ruta_salida = os.path.join(output_folder, f"{nombre}_comprimido{ext}")
    imagen_redimensionada.save(ruta_salida, format="JPEG", quality=quality,
                               icc_profile=imagen_original.info.get('icc_profile'))
    return ruta_salida


class CompressorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compresor de Imágenes")

        # Marco para la calidad de la imagen
        self.quality_frame = ttk.LabelFrame(self, text="Calidad de la imagen")
        self.quality_frame.pack(padx=10, pady=10, fill=tk.X)

        self.quality_var = tk.StringVar(value="50")
        self.quality_slider = ttk.Scale(self.quality_frame, from_=1, to_=100, orient=tk.HORIZONTAL,
                                        variable=self.quality_var, command=self.update_quality_entry)
        self.quality_slider.pack(padx=10, pady=5, fill=tk.X)

        self.quality_entry = ttk.Entry(
            self.quality_frame, textvariable=self.quality_var, width=4)
        self.quality_entry.pack(padx=10, pady=5, side=tk.LEFT)
        self.quality_entry.bind("<Return>", self.update_quality_slider)
        self.quality_entry.bind("<FocusOut>", self.update_quality_slider)

        # Marco para las opciones de redimensionamiento
        self.resize_frame = ttk.LabelFrame(
            self, text="Opción de redimensionamiento")
        self.resize_frame.pack(padx=10, pady=10, fill=tk.X)

        self.resize_var = tk.StringVar(value="percentage")
        self.percentage_rb = ttk.Radiobutton(self.resize_frame, text="Por Porcentaje",
                                             value="percentage", variable=self.resize_var, command=self.toggle_resize_option)
        self.percentage_rb.pack(anchor=tk.W, padx=10, pady=5)

        self.dimension_rb = ttk.Radiobutton(self.resize_frame, text="Por Dimensiones",
                                            value="dimension", variable=self.resize_var, command=self.toggle_resize_option)
        self.dimension_rb.pack(anchor=tk.W, padx=10, pady=5)

        self.percentage_entry = ttk.Entry(self.resize_frame)
        self.width_label = ttk.Label(self.resize_frame, text="Ancho:")
        self.width_entry = ttk.Entry(self.resize_frame)
        self.height_label = ttk.Label(self.resize_frame, text="Alto:")
        self.height_entry = ttk.Entry(self.resize_frame)

        # Marco para los botones
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(padx=10, pady=10, fill=tk.X)

        self.select_folder_button = ttk.Button(
            self.button_frame, text="Seleccionar Carpeta", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT, padx=10)

        self.compress_button = ttk.Button(
            self.button_frame, text="Comprimir", command=self.compress_images, state=tk.DISABLED)
        self.compress_button.pack(side=tk.RIGHT, padx=10)

        # Inicializar
        self.toggle_resize_option()

        # Agregar Progressbar
        self.progress = ttk.Progressbar(
            self, orient=tk.HORIZONTAL, mode='determinate')

        # Inicialmente, la barra de progreso no se mostrará


        # Agregar botón Cancelar que inicialmente estará oculto
        self.cancel_button = ttk.Button(
            self.button_frame, text="Cancelar", command=self.cancel_compression)
        self.cancel_event = threading.Event()

        # Modificar cómo se empaca el botón y la barra de progreso
        self.select_folder_button.pack(pady=10)
        self.compress_button.pack(pady=10)

    def update_progress(self, increment):
        """Actualiza la barra de progreso"""
        self.progress['value'] += increment
        self.update_idletasks()

    def update_quality_entry(self, event=None):
        """Actualiza el campo de entrada de calidad según el valor del deslizador"""
        self.quality_var.set(round(self.quality_slider.get()))

    def update_quality_slider(self, event=None):
        """Actualiza el deslizador de calidad según el valor en el campo de entrada"""
        try:
            value = int(self.quality_var.get())
            if 1 <= value <= 100:
                self.quality_slider.set(value)
            else:
                self.quality_var.set(self.quality_slider.get())
        except ValueError:
            self.quality_var.set(self.quality_slider.get())

    def toggle_resize_option(self):
        """Ajusta los campos de entrada según la opción de redimensionamiento seleccionada"""
        if self.resize_var.get() == "percentage":
            self.percentage_entry.pack(padx=10, pady=5)
            self.width_label.pack_forget()
            self.width_entry.pack_forget()
            self.height_label.pack_forget()
            self.height_entry.pack_forget()
        else:
            self.percentage_entry.pack_forget()
            self.width_label.pack(padx=10, pady=5, anchor=tk.W)
            self.width_entry.pack(padx=10, pady=5)
            self.height_label.pack(padx=10, pady=5, anchor=tk.W)
            self.height_entry.pack(padx=10, pady=5)

    def select_folder(self):
        self.compress_button.config(state=tk.NORMAL)
        """Permite al usuario seleccionar una carpeta con imágenes"""
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
        self.compress_button.config(state=tk.NORMAL)

    def compress_images(self):
        """Comprime las imágenes según las opciones seleccionadas"""
        # Obtener las opciones de compresión
        quality = int(self.quality_var.get())
        if self.resize_var.get() == "percentage":
            resize_option = "percentage"
            scale_percentage = float(self.percentage_entry.get()) / 100.0
        else:
            resize_option = "dimension"
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())

        # Listar todas las imágenes en la carpeta seleccionada
        imagenes = [os.path.join(self.selected_folder, nombre) for nombre in os.listdir(
            self.selected_folder) if os.path.splitext(nombre)[1].lower() in [".jpg", ".jpeg"]]

        # Mostrar la barra de progreso antes de iniciar la compresión
        self.progress.pack(pady=10, padx=10, fill=tk.X)  # Se agregó padx=10

        # Inicializar la barra de progreso
        self.progress['value'] = 0
        self.progress['maximum'] = len(imagenes)

        # Mostrar el botón Cancelar
        self.cancel_button.pack(pady=10)
        # Restablecer el evento de cancelación
        self.cancel_event.clear()

        def worker():
            # Usar un bucle for con as_completed para manejar las tareas completadas
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(comprimir_imagen, img, self.selected_folder, quality, resize_option, scale_percentage if resize_option ==
                                           "percentage" else width, scale_percentage if resize_option == "percentage" else height, self.cancel_event) for img in imagenes]
                for future in as_completed(futures):
                    if self.cancel_event.is_set():
                        break
                    self.after(0, self.update_progress, 1)

            # Ocultar el botón Cancelar
            self.cancel_button.pack_forget()
    


            if self.cancel_event.is_set():
                messagebox.showwarning(
                    "Advertencia", "Proceso cancelado por el usuario.")
            else:
                messagebox.showinfo("Info", "¡Compresión completada!")

            # Abre la carpeta "comprimido"
            webbrowser.open(os.path.join(self.selected_folder, 'comprimido'))

        threading.Thread(target=worker).start()
        

    def cancel_compression(self):
        """Maneja la solicitud de cancelación del usuario"""
        answer = messagebox.askyesno(
            "Confirmación", "¿Está seguro de que desea cancelar el proceso?")
        if answer:
            self.cancel_event.set()


if __name__ == "__main__":
    app = CompressorApp()
    app.mainloop()
