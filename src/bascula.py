import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import requests
from datetime import datetime
import configparser
import os
import sys

class BasculaApp:
    def __init__(self, root):
        self.root = root
        self.cargar_configuracion()
        self.root.title(self.config.get('APP', 'title', fallback='BASCULA SERVITECA-PC'))
        self.root.geometry("400x300")

        # Establecer ícono
        if getattr(sys, 'frozen', False):
            # Estamos en el ejecutable
            application_path = sys._MEIPASS
        else:
            # Estamos en desarrollo
            application_path = os.path.dirname(os.path.abspath(__file__))

        try:
            icon_path = os.path.join(application_path, 'assets', 'icon.ico')
            self.root.iconbitmap(icon_path)
        except:
            pass  # Si no encuentra el ícono, continúa sin él

        self.puerto_serial = None
        self.crear_interfaz()
        self.buscar_puertos()

    def cargar_configuracion(self):
        """Carga la configuración desde config.ini"""
        self.config = configparser.ConfigParser()
        if getattr(sys, 'frozen', False):
            # Estamos en el ejecutable
            config_path = os.path.join(sys._MEIPASS, 'config.ini')
        else:
            # Estamos en desarrollo
            config_path = 'config.ini'

        self.config.read(config_path)

    def crear_interfaz(self):
        # Estilo
        style = ttk.Style()
        style.configure('Big.TButton', font=('Arial', 12, 'bold'))

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Puerto Serial
        ttk.Label(main_frame, text="Puerto:").grid(row=0, column=0, sticky="w")
        self.puerto_combo = ttk.Combobox(main_frame, width=20)
        self.puerto_combo.grid(row=0, column=1, padx=5, sticky="ew")

        self.btn_conectar = ttk.Button(
            main_frame,
            text="Conectar",
            command=self.conectar_puerto
        )
        self.btn_conectar.grid(row=0, column=2, padx=5)

        # Display de peso
        self.visor_peso = ttk.Label(
            main_frame,
            text="0.0 Kg",
            font=('Arial', 24, 'bold')
        )
        self.visor_peso.grid(row=1, column=0, columnspan=3, pady=20)

        # Botón tomar peso
        self.btn_tomar_peso = ttk.Button(
            main_frame,
            text="TOMAR PESO",
            command=self.tomar_peso,
            style='Big.TButton'
        )
        self.btn_tomar_peso.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

        # Estado
        self.estado_label = ttk.Label(main_frame, text="Estado: Desconectado")
        self.estado_label.grid(row=3, column=0, columnspan=3, pady=5)

    def buscar_puertos(self):
        puertos = [port.device for port in serial.tools.list_ports.comports()]
        self.puerto_combo['values'] = puertos
        if puertos:
            self.puerto_combo.set(puertos[0])

    def conectar_puerto(self):
        try:
            if self.puerto_serial and self.puerto_serial.is_open:
                self.puerto_serial.close()
                self.btn_conectar.config(text="Conectar")
                self.estado_label.config(text="Estado: Desconectado")
                return

            puerto = self.puerto_combo.get()
            self.puerto_serial = serial.Serial(
                port=puerto,
                baudrate=self.config.getint('SERIAL', 'baudrate', fallback=9600),
                timeout=self.config.getint('SERIAL', 'timeout', fallback=1)
            )

            self.btn_conectar.config(text="Desconectar")
            self.estado_label.config(text="Estado: Conectado")

        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {str(e)}")
            self.estado_label.config(text="Estado: Error")

    def tomar_peso(self):
        try:
             if not self.puerto_serial or not self.puerto_serial.is_open:
                 messagebox.showerror("Error", "Puerto no conectado")
                 return

             self.puerto_serial.reset_input_buffer()
             datos = self.puerto_serial.readline().decode().strip()

             #Procesar datos según el formato de tu báscula
             peso = datos.replace("LG", "").replace("Z", "").strip()

             self.visor_peso.config(text=f"{peso} Kg")
             self.enviar_a_api(peso)

        except Exception as e:
            messagebox.showerror("Error", f"Error al leer peso: {str(e)}")

    def enviar_a_api(self, peso):
        try:
            url = self.config.get('API', 'url')
            datos = {
                "nombreMaquina" :  "BASCULAPT",
                "peso": peso,
                "contador": 17,
            }

            response = requests.post(url, json=datos, timeout=5)

            if response.status_code == 200:
                self.estado_label.config(text="Estado: Datos enviados")
            else:
                raise Exception(f"Error {response.status_code}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar datos: {str(e)}")
            self.estado_label.config(text="Estado: Error al enviar")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = BasculaApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Error al iniciar la aplicación: {str(e)}")