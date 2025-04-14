import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from colorama import init, Fore, Back, Style
import keyboard

# Inicializar colorama
init(autoreset=True)

class ProductorConsumidorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tania-Said-Productor-Consumidor-UAESO")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configuración del buffer circular
        self.buffer_size = 25
        self.buffer = ["_"] * self.buffer_size
        self.productor_index = 0
        self.consumidor_index = 0
        self.elementos_en_buffer = 0
        
        # Semáforos
        self.mutex = threading.Semaphore(1)  # Para exclusión mutua
        self.espacios_vacios = threading.Semaphore(self.buffer_size)  # Controla espacios vacíos
        self.productos_disponibles = threading.Semaphore(0)  # Controla productos disponibles
        
        # Estados
        self.productor_estado = "Dormido"
        self.consumidor_estado = "Dormido"
        self.productor_mensaje = ""
        self.consumidor_mensaje = ""
        
        # Banderas para controlar hilos
        self.ejecutando = True
        
        # Configuración de la interfaz
        self.setup_ui()
        
        # Iniciar hilos
        self.productor_thread = threading.Thread(target=self.productor_process)
        self.consumidor_thread = threading.Thread(target=self.consumidor_process)
        self.update_thread = threading.Thread(target=self.update_ui_thread)
        
        self.productor_thread.daemon = True
        self.consumidor_thread.daemon = True
        self.update_thread.daemon = True
        
        self.productor_thread.start()
        self.consumidor_thread.start()
        self.update_thread.start()
        
        # Monitorear la tecla Escape para salir
        keyboard.on_press_key("esc", self.on_esc_pressed)
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para el buffer
        buffer_frame = ttk.LabelFrame(main_frame, text="Buffer (capacidad: 25)", padding="10")
        buffer_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Crear celdas para el buffer
        self.buffer_cells = []
        buffer_container = ttk.Frame(buffer_frame)
        buffer_container.pack(fill=tk.X)
        
        for i in range(self.buffer_size):
            cell_frame = ttk.Frame(buffer_container, borderwidth=1, relief="solid", width=20, height=30)
            cell_frame.grid(row=0, column=i, padx=1)
            cell_frame.grid_propagate(False)
            
            # Etiqueta para la celda del buffer
            cell_label = ttk.Label(cell_frame, text="_", anchor="center")
            cell_label.pack(fill=tk.BOTH, expand=True)
            self.buffer_cells.append(cell_label)
            
            # Etiqueta para el número de posición
            pos_label = ttk.Label(buffer_container, text=str(i+1), anchor="center", width=3)
            pos_label.grid(row=1, column=i)
        
        # Frame para la información del productor y consumidor
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Información del productor
        productor_frame = ttk.LabelFrame(info_frame, text="Productor", padding="10")
        productor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(productor_frame, text="Estado:").grid(row=0, column=0, sticky="w", pady=5)
        self.productor_estado_label = ttk.Label(productor_frame, text="Dormido")
        self.productor_estado_label.grid(row=0, column=1, sticky="w", pady=5)
        
        ttk.Label(productor_frame, text="Mensaje:").grid(row=1, column=0, sticky="w", pady=5)
        self.productor_mensaje_label = ttk.Label(productor_frame, text="")
        self.productor_mensaje_label.grid(row=1, column=1, sticky="w", pady=5)
        
        ttk.Label(productor_frame, text="Posición actual:").grid(row=2, column=0, sticky="w", pady=5)
        self.productor_pos_label = ttk.Label(productor_frame, text="1")
        self.productor_pos_label.grid(row=2, column=1, sticky="w", pady=5)
        
        # Información del consumidor
        consumidor_frame = ttk.LabelFrame(info_frame, text="Consumidor", padding="10")
        consumidor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(consumidor_frame, text="Estado:").grid(row=0, column=0, sticky="w", pady=5)
        self.consumidor_estado_label = ttk.Label(consumidor_frame, text="Dormido")
        self.consumidor_estado_label.grid(row=0, column=1, sticky="w", pady=5)
        
        ttk.Label(consumidor_frame, text="Mensaje:").grid(row=1, column=0, sticky="w", pady=5)
        self.consumidor_mensaje_label = ttk.Label(consumidor_frame, text="")
        self.consumidor_mensaje_label.grid(row=1, column=1, sticky="w", pady=5)
        
        ttk.Label(consumidor_frame, text="Posición actual:").grid(row=2, column=0, sticky="w", pady=5)
        self.consumidor_pos_label = ttk.Label(consumidor_frame, text="1")
        self.consumidor_pos_label.grid(row=2, column=1, sticky="w", pady=5)
        
        # Información general
        general_frame = ttk.LabelFrame(main_frame, text="Información General", padding="10")
        general_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(general_frame, text="Elementos en buffer:").grid(row=0, column=0, sticky="w", pady=5)
        self.elementos_label = ttk.Label(general_frame, text="0/25")
        self.elementos_label.grid(row=0, column=1, sticky="w", pady=5)
        
        ttk.Label(general_frame, text="Estado:").grid(row=1, column=0, sticky="w", pady=5)
        self.estado_general_label = ttk.Label(general_frame, text="Ejecutando...")
        self.estado_general_label.grid(row=1, column=1, sticky="w", pady=5)
        
        # Instrucciones
        instrucciones_frame = ttk.LabelFrame(main_frame, text="Instrucciones", padding="10")
        instrucciones_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(instrucciones_frame, text="Presione ESC para terminar el programa").pack(pady=5)
    
    def productor_process(self):
        """Proceso del productor"""
        while self.ejecutando:
            # Dormir por un tiempo aleatorio
            sleep_time = random.uniform(0.5, 3)
            self.productor_estado = f"Dormido por {sleep_time:.2f}s"
            self.productor_mensaje = "ZZZ..."
            print(f"{Fore.YELLOW}Productor: {self.productor_estado}")
            time.sleep(sleep_time)
            
            # Despertar e intentar producir
            items_to_produce = random.randint(1, 5)
            self.productor_estado = f"Despierto, intentando producir {items_to_produce} elementos"
            self.productor_mensaje = f"Quiero producir {items_to_produce} elementos"
            print(f"{Fore.GREEN}Productor: {self.productor_estado}")
            
            for _ in range(items_to_produce):
                # Esperar a que haya espacio vacío
                if not self.espacios_vacios.acquire(blocking=False):
                    self.productor_mensaje = "Esperando espacio disponible..."
                    print(f"{Fore.RED}Productor: Buffer lleno, esperando espacio...")
                    self.espacios_vacios.acquire()  # Bloqueante
                    
                # Adquirir mutex para exclusión mutua
                self.mutex.acquire()
                
                try:
                    # Producir un elemento
                    self.productor_estado = "Trabajando"
                    self.productor_mensaje = f"Produciendo en posición {self.productor_index + 1}"
                    print(f"{Fore.CYAN}Productor: Produciendo en posición {self.productor_index + 1}")
                    
                    # Colocar producto en el buffer
                    self.buffer[self.productor_index] = "*"
                    
                    # Actualizar índice del productor
                    self.productor_index = (self.productor_index + 1) % self.buffer_size
                    self.elementos_en_buffer += 1
                    
                    # Esperar un poco para visualizar el cambio
                    time.sleep(0.3)
                finally:
                    # Liberar mutex
                    self.mutex.release()
                    
                # Señalar que hay un producto disponible
                self.productos_disponibles.release()
                
            self.productor_mensaje = f"Terminé de producir {items_to_produce} elementos"
            print(f"{Fore.GREEN}Productor: Terminé de producir {items_to_produce} elementos")
            time.sleep(0.5)
    
    def consumidor_process(self):
        """Proceso del consumidor"""
        while self.ejecutando:
            # Dormir por un tiempo aleatorio
            sleep_time = random.uniform(0.5, 3)
            self.consumidor_estado = f"Dormido por {sleep_time:.2f}s"
            self.consumidor_mensaje = "ZZZ..."
            print(f"{Fore.YELLOW}Consumidor: {self.consumidor_estado}")
            time.sleep(sleep_time)
            
            # Despertar e intentar consumir
            items_to_consume = random.randint(1, 5)
            self.consumidor_estado = f"Despierto, intentando consumir {items_to_consume} elementos"
            self.consumidor_mensaje = f"Quiero consumir {items_to_consume} elementos"
            print(f"{Fore.BLUE}Consumidor: {self.consumidor_estado}")
            
            for _ in range(items_to_consume):
                # Esperar a que haya productos disponibles
                if not self.productos_disponibles.acquire(blocking=False):
                    self.consumidor_mensaje = "Esperando que haya productos..."
                    print(f"{Fore.RED}Consumidor: Buffer vacío, esperando productos...")
                    self.productos_disponibles.acquire()  # Bloqueante
                
                # Adquirir mutex para exclusión mutua
                self.mutex.acquire()
                
                try:
                    # Consumir un elemento
                    self.consumidor_estado = "Trabajando"
                    self.consumidor_mensaje = f"Consumiendo de posición {self.consumidor_index + 1}"
                    print(f"{Fore.MAGENTA}Consumidor: Consumiendo de posición {self.consumidor_index + 1}")
                    
                    # Quitar producto del buffer
                    self.buffer[self.consumidor_index] = "_"
                    
                    # Actualizar índice del consumidor
                    self.consumidor_index = (self.consumidor_index + 1) % self.buffer_size
                    self.elementos_en_buffer -= 1
                    
                    # Esperar un poco para visualizar el cambio
                    time.sleep(0.3)
                finally:
                    # Liberar mutex
                    self.mutex.release()
                
                # Señalar que hay un espacio vacío
                self.espacios_vacios.release()
            
            self.consumidor_mensaje = f"Terminé de consumir {items_to_consume} elementos"
            print(f"{Fore.BLUE}Consumidor: Terminé de consumir {items_to_consume} elementos")
            time.sleep(0.5)
    
    def update_ui_thread(self):
        """Hilo para actualizar la interfaz de usuario"""
        while self.ejecutando:
            try:
                self.update_ui()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error al actualizar UI: {e}")
    
    def update_ui(self):
        """Actualizar la interfaz de usuario"""
        # Actualizar buffer
        for i in range(self.buffer_size):
            self.buffer_cells[i].config(text=self.buffer[i])
            if self.buffer[i] == "*":
                self.buffer_cells[i]["foreground"] = "green"
            else:
                self.buffer_cells[i]["foreground"] = "black"
        
        # Actualizar información del productor
        self.productor_estado_label.config(text=self.productor_estado)
        self.productor_mensaje_label.config(text=self.productor_mensaje)
        self.productor_pos_label.config(text=str(self.productor_index + 1))
        
        # Actualizar información del consumidor
        self.consumidor_estado_label.config(text=self.consumidor_estado)
        self.consumidor_mensaje_label.config(text=self.consumidor_mensaje)
        self.consumidor_pos_label.config(text=str(self.consumidor_index + 1))
        
        # Actualizar información general
        self.elementos_label.config(text=f"{self.elementos_en_buffer}/{self.buffer_size}")
    
    def on_esc_pressed(self, event):
        """Manejar cuando se presiona ESC"""
        self.ejecutando = False
        self.root.after(100, self.root.destroy)
    
    def on_closing(self):
        """Manejar el cierre de la ventana"""
        self.ejecutando = False
        self.root.destroy()

def main():
    print(f"{Fore.CYAN}Iniciando el programa Productor-Consumidor")
    print(f"{Fore.YELLOW}Presione ESC para finalizar el programa")
    
    root = tk.Tk()
    app = ProductorConsumidorApp(root)
    root.mainloop()
    
    print(f"{Fore.RED}Programa finalizado")

if __name__ == "__main__":
    main()