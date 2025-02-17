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
        # Inicializar configuración por defecto
        self.config = configparser.ConfigParser()
        self.config['APP'] = {
            'title': 'BASCULA SERVITECA-PC'
        }
        self.config['SERIAL'] = {
            'baudrate': '9600',
            'timeout': '1'
        }
        self.config['API'] = {
            'url': 'http://localhost:3001/transporte/grabaPeso/'
        }

        self.root.title(self.config['APP']['title'])
        self.root.geometry("400x300")

        # Variables para monitoreo en tiempo real
        self.is_monitoring = False
        self.last_weight = "0.0"
        self.update_interval = 100  # 100ms = 10 actualizaciones por segundo

        # Establecer ícono
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        try:
            icon_path = os.path.join(application_path, 'assets', 'icon.ico')
            self.root.iconbitmap(icon_path)
        except:
            pass

        self.puerto_serial = None
        self.crear_interfaz()
        self.buscar_puertos()

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

        # Switch para lectura en tiempo real
        self.monitoring_var = tk.BooleanVar(value=False)
        self.monitoring_switch = ttk.Checkbutton(
            main_frame,
            text="Lectura en tiempo real",
            variable=self.monitoring_var,
            command=self.toggle_monitoring
        )
        self.monitoring_switch.grid(row=2, column=0, columnspan=3, pady=5)

        # Botón tomar peso
        self.btn_tomar_peso = ttk.Button(
            main_frame,
            text="TOMAR PESO",
            command=self.tomar_peso,
            style='Big.TButton'
        )
        self.btn_tomar_peso.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

        # Estado
        self.estado_label = ttk.Label(main_frame, text="Estado: Desconectado")
        self.estado_label.grid(row=4, column=0, columnspan=3, pady=5)

    def toggle_monitoring(self):
        """Activa o desactiva el monitoreo en tiempo real"""
        if self.monitoring_var.get():
            if not self.puerto_serial or not self.puerto_serial.is_open:
                messagebox.showerror("Error", "Primero conecte el puerto serial")
                self.monitoring_var.set(False)
                return
            self.is_monitoring = True
            self.estado_label.config(text="Estado: Monitoreando")
            self.update_weight_reading()
        else:
            self.is_monitoring = False
            self.estado_label.config(text="Estado: Conectado")

    def update_weight_reading(self):
        """Actualiza la lectura del peso en tiempo real"""
        if self.is_monitoring:
            try:
                if self.puerto_serial.in_waiting:
                    self.puerto_serial.reset_input_buffer()
                    datos = self.puerto_serial.readline().decode().strip()
                    peso = datos.replace("LG", "").replace("Z", "").strip()

                    if peso != self.last_weight:  # Solo actualizar si el peso cambió
                        self.last_weight = peso
                        self.visor_peso.config(text=f"{peso} Kg")
                        # Opcional: enviar automáticamente a la API
                        # self.enviar_a_api(peso)
            except Exception as e:
                self.monitoring_var.set(False)
                self.is_monitoring = False
                messagebox.showerror("Error", str(e))
                return

            # Programar la próxima actualización
            self.root.after(self.update_interval, self.update_weight_reading)

    def buscar_puertos(self):
        puertos = [port.device for port in serial.tools.list_ports.comports()]
        self.puerto_combo['values'] = puertos
        if puertos:
            self.puerto_combo.set(puertos[0])

    def conectar_puerto(self):
        try:
            if self.puerto_serial and self.puerto_serial.is_open:
                self.monitoring_var.set(False)
                self.is_monitoring = False
                self.puerto_serial.close()
                self.btn_conectar.config(text="Conectar")
                self.estado_label.config(text="Estado: Desconectado")
                return

            puerto = self.puerto_combo.get()
            self.puerto_serial = serial.Serial(
                port=puerto,
                baudrate=int(self.config['SERIAL']['baudrate']),
                timeout=int(self.config['SERIAL']['timeout'])
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
            peso = datos.replace("LG", "").replace("Z", "").strip()

            self.visor_peso.config(text=f"{peso} Kg")
            self.enviar_a_api(peso)

        except Exception as e:
            messagebox.showerror("Error", f"Error al leer peso: {str(e)}")

    def enviar_a_api(self, peso):
        try:
            url = self.config['API']['url']
            datos = {
                "nombreMaquina": "BASCULAPT",
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