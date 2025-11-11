# models/interfaz.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
from contextlib import redirect_stdout
from sympy import sympify, symbols, pretty
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy

# Acrónimo de 'Regular Expressions'. Utilizada para que sea más fácil ingresar ecuaciones
import re

from fractions import Fraction

from models.vectoresMatrices.eliminacion import eliminacionGaussJordan, eliminacionGauss
from models.vectoresMatrices.operaciones import suma_matrices, multiplicar_matrices
from models.vectoresMatrices.transpuesta import transpuestamatriz
from models.vectoresMatrices.independencia import independenciaLineal
from models.vectoresMatrices.inversa import inversaMatriz
from models.determinantes.determinante import detMatriz
from models.determinantes.cramer import reglaCramer
from models.biseccion import metodoBiseccion

from models.imprimir_matriz import imprimir_matriz

class _TextRedirector:
    """Redirige cadenas a un Text widget (para capturar print/print_func)."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, s):
        if not s:
            return
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, s)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state="disabled")
        except tk.TclError:
            pass

    def flush(self):
        return

class Interfaz:
    
    # VENTANA PRINCIPAL
    def __init__(self):

        self.menuPrincipal = tk.Tk()
        self.menuPrincipal.title("Calculadora NumExpert")
        self.menuPrincipal.geometry("600x450")
        self.menuPrincipal.resizable(width=False, height=False)

        # Configuración de estilos (tema y apariencia)
        # Usamos ttk.Style para aplicar una apariencia más moderna y coherente
        style = ttk.Style(self.menuPrincipal)
        try:
            # 'clam' suele permitir más personalización en Windows y Linux
            style.theme_use('clam')
        except Exception:
            pass
        
        # Tipografías y colores base
        default_font = ('Segoe UI', 10)
        label_font = ('Helvetica', 10)
        
        # Configuraciones generales
        style.configure('TLabel', font=label_font, background='#0b5c71', foreground='#e6e6e6')
        style.configure('TFrame', background='#0b5c71')
        style.configure('TButton', font=default_font, padding=6)
        style.configure('TEntry', font=default_font)
        style.configure('TCombobox', font=default_font)
        
        # Botón destacado
        style.configure('Accent.TButton', font=default_font, padding=8, foreground='#e6e6e6', background='#3b8b87')
        style.map('Accent.TButton', background=[('active', '#0d6462'), ('!disabled', '#3b8b87')])
        
        # Fondo de la ventana
        try:
            self.menuPrincipal.configure(background='#0b5c71')
        except Exception:
            pass

        ttk.Label(self.menuPrincipal, text="Bienvenido a NumExpert", font=('Cambria Math', 24, 'bold')).grid(row=0, column=0, padx=105)
        ttk.Label(self.menuPrincipal, text="Seleccione una opción", font=('Times New Roman', 12)).grid(row=1,column=0)

        ttk.Button(self.menuPrincipal, text="Álgebra Lineal", padding=7, command=lambda: [self.menuPrincipal.wm_withdraw(), self.algebraLineal()]).grid(row=2, column=0, pady=8)
        ttk.Button(self.menuPrincipal, text="Análisis Númerico", padding=7, command=lambda: [self.menuPrincipal.wm_withdraw(), self.analisisNumerico()]).grid(row=3, column=0, pady=8)

        ttk.Label(self.menuPrincipal, text="© Copyright 2025 - 2025", font=('Times New Roman', 12)).grid(row=5, column=0, pady=7)
    
    def algebraLineal(self):
        
        self.ventanaPrincipal = Toplevel(self.menuPrincipal)
        self.ventanaPrincipal.title("NumExpert (Álgebra Lineal)")
        self.ventanaPrincipal.geometry("1350x720")
        self.ventanaPrincipal.resizable(width=False, height=False)
        # Abrir la ventana maximizada por defecto. En Windows se usa 'zoomed';
        # como fallback intentamos el atributo '-zoomed' (algunos entornos X11 lo soportan).
        try:
            self.ventanaPrincipal.state('zoomed')
        except Exception:
            try:
                self.ventanaPrincipal.attributes('-zoomed', True)
            except Exception:
                # No se pudo maximizar automáticamente; se mantiene la geometría por defecto
                pass

        self.ventanaPrincipal.configure(background='#0b5c71')

        # Configuración de estilos (tema y apariencia)
        # Usamos ttk.Style para aplicar una apariencia más moderna y coherente
        style = ttk.Style(self.ventanaPrincipal)
        try:
            # 'clam' suele permitir más personalización en Windows y Linux
            style.theme_use('clam')
        except Exception:
            pass
        # Tipografías y colores base
        default_font = ('Segoe UI', 10)
        label_font = ('Helvetica', 10)
        # Configuraciones generales
        style.configure('TLabel', font=label_font, background='#0b5c71', foreground='#e6e6e6')
        style.configure('TFrame', background='#0b5c71')
        style.configure('TButton', font=default_font, padding=6)
        style.configure('TEntry', font=default_font)
        style.configure('TCombobox', font=default_font)
        # Botón destacado
        style.configure('Accent.TButton', font=default_font, padding=8, foreground='#e6e6e6', background='#3b8b87')
        style.map('Accent.TButton', background=[('active', '#0d6462'), ('!disabled', '#3b8b87')])
        # Resultado
        style.configure('Result.TLabel', background='white', padding=6, font=default_font)
        # Fondo de la ventana
        try:
            self.ventanaPrincipal.configure(background='#0b5c71')
        except Exception:
            pass

        # Variables
        self.metodo = tk.StringVar(value="")
        self.num_eq_var = tk.StringVar(value="")
        self.num_var_var = tk.StringVar(value="")
        self.matA_filas = tk.StringVar(value="")
        self.matA_columnas = tk.StringVar(value="")
        self.matA_escalar = tk.StringVar(value="")
        self.matB_filas = tk.StringVar(value="")
        self.matB_columnas = tk.StringVar(value="")
        self.matB_escalar = tk.StringVar(value="")
        self.metodoEscoger = tk.StringVar(value="(Elija un método)")

        # Grids de entrada
        self.entradas_aug = []
        self.entradas_A = []
        self.entradas_B = []

        self._build_ui()

    def analisisNumerico(self):
        self.ventanaPrincipal_AN = Toplevel(self.menuPrincipal)
        self.ventanaPrincipal_AN.title("NumExpert (Análisis Numérico)")
        self.ventanaPrincipal_AN.geometry("1350x720")
        self.ventanaPrincipal_AN.resizable(width=False, height=False)

        # Abrir la ventana maximizada por defecto. En Windows se usa 'zoomed';
        # como fallback intentamos el atributo '-zoomed' (algunos entornos X11 lo soportan).
        try:
            
            self.ventanaPrincipal_AN.state('zoomed')
        except Exception:
            try:
                
                self.ventanaPrincipal_AN.attributes('-zoomed', True)
            except Exception:
                
                # No se pudo maximizar automáticamente; se mantiene la geometría por defecto
                pass

        # Configuración de estilos (tema y apariencia)
        # Usamos ttk.Style para aplicar una apariencia más moderna y coherente
        style = ttk.Style(self.menuPrincipal)
        try:
            # 'clam' suele permitir más personalización en Windows y Linux
            style.theme_use('clam')
        except Exception:
            pass
        
        # Tipografías y colores base
        default_font = ('Segoe UI', 10)
        label_font = ('Helvetica', 10)
        
        # Configuraciones generales
        style.configure('TLabel', font=label_font, background='#0b5c71', foreground='#e6e6e6')
        style.configure('TFrame', background='#0b5c71')
        style.configure('TButton', font=default_font, padding=6)
        style.configure('TEntry', font=default_font)
        style.configure('TCombobox', font=default_font)
        
        # Botón destacado
        style.configure('Accent.TButton', font=default_font, padding=8, foreground='#e6e6e6', background='#3b8b87')
        style.map('Accent.TButton', background=[('active', '#0d6462'), ('!disabled', '#3b8b87')])

        # Variables
        self.metodoNum = tk.StringVar(value="(Elige un método)")
        self.ecuacionEntrada = tk.StringVar(value="")
        self.limInf = tk.StringVar(value="")
        self.limSup = tk.StringVar(value="")

        metodos = ttk.Frame(self.ventanaPrincipal_AN, padding=8)
        metodos.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(metodos, text="Métodos Cerrados", width=25, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(metodos, text="Volver al menú", width=25, command=lambda: [self.ventanaPrincipal_AN.wm_withdraw(), self.menuPrincipal.wm_deiconify()], style='Accent.TButton').pack(side=tk.RIGHT, padx=5)

        izquierda = ttk.Frame(self.ventanaPrincipal_AN, style='TFrame')
        izquierda.pack(side=tk.LEFT, fill=tk.BOTH)

        ttk.Label(izquierda, text="Ingrese la ecuación:").grid(row=0,column=0,pady=10, padx=5)
        self.ecuacion = ttk.Entry(izquierda, width=52)
        self.ecuacion.grid(row=1,column=0,pady=10)

        ttk.Button(izquierda, text="Graficar función", command=self.graficarFuncion, width=42, style='Accent.TButton').grid(row=2,column=0,pady=5, padx=5)

        ttk.Label(izquierda, text="Método para resolver la ecuación").grid(row=3,column=0, pady=10)
        self.metodosCerrados = ttk.Combobox(izquierda, textvariable=self.metodoNum, values=('Método de bisección', 'Método de falsa posición'), width=30)
        self.metodosCerrados.grid(row=4, column=0, pady=8)
        self.metodosCerrados.state(['readonly'])

        # Botones para mejorar la escritura de la ecuación
        botonesEcuacion = ttk.Frame(izquierda, padding=10)
        botonesEcuacion.grid(row=5,column=0)

        # 1er fila de botones
        ttk.Button(botonesEcuacion, text="^", command=lambda: self.ecuacion.insert(self.ecuacion.index(tk.INSERT),'^'), style='Accent.TButton').grid(row=0,column=0,pady=5, padx=5)
        ttk.Button(botonesEcuacion, text="e", command=lambda: self.ecuacion.insert(self.ecuacion.index(tk.INSERT), 'e'), style='Accent.TButton').grid(row=0,column=1,pady=5, padx=5)
        ttk.Button(botonesEcuacion, text="π", command=lambda: self.ecuacion.insert(self.ecuacion.index(tk.INSERT), 'π'), style='Accent.TButton').grid(row=0,column=2,pady=5, padx=5)

        # 2da fila de botones
        ttk.Button(botonesEcuacion, text="sin(x)", command=lambda: self.ecuacion.insert(self.ecuacion.index(tk.INSERT),'sin(x)'), style='Accent.TButton').grid(row=1,column=0,pady=5, padx=5)
        ttk.Button(botonesEcuacion, text="cos(x)", command=lambda: self.ecuacion.insert(self.ecuacion.index(tk.INSERT),'cos(x)'), style='Accent.TButton').grid(row=1,column=1,pady=5, padx=5)
        ttk.Button(botonesEcuacion, text="tan(x)", command=lambda: self.ecuacion.insert(self.ecuacion.index(tk.INSERT),'tan(x)'), style='Accent.TButton').grid(row=1,column=2,pady=5, padx=5)

        # Entradas del intervalo
        intervaloRaiz = ttk.Frame(izquierda, padding=10)
        intervaloRaiz.grid(row=6,column=0)

        ttk.Label(intervaloRaiz, text="Intervalo para encontrar la raíz").pack(anchor='center')
        
        ttk.Label(intervaloRaiz, text="Límite Inferior (A)").pack(anchor='w', pady=4)
        self.limI = ttk.Entry(intervaloRaiz, width=30)
        self.limI.pack(anchor='center', pady=2)

        ttk.Label(intervaloRaiz, text="Límite Superior (B)").pack(anchor='w', pady=4)
        self.limS = ttk.Entry(intervaloRaiz, width=30)
        self.limS.pack(anchor='center', pady=2)

        ttk.Button(intervaloRaiz, text="Encontrar Respuesta", command=self.resolverEcuacion, style='Accent.TButton').pack(anchor='center', pady=7)

        # PROCEDIMIENTO Y RESULTADOS
        self.procedimiento = ttk.Frame(self.ventanaPrincipal_AN)
        self.procedimiento.pack(side=tk.TOP, fill=tk.BOTH)
        ttk.Label(self.procedimiento, text="RESULTADOS:", font=(None,10,'bold'), background='#0b5c71', foreground='#e6e6e6').pack(anchor='w')

        # TABLA TREEVIEW
        self.tablaTrv = ttk.Treeview(self.procedimiento, columns=("#", "Límite Inferior (A)", "Límite Superior (B)", "Punto Medio (C)", "Error (Ea)", "F(A)", "F(B)", "F(C)"), show='headings')
        self.tablaTrv.heading("#", text="#")
        self.tablaTrv.column("#", width=30, anchor='center')
        for col in ("Límite Inferior (A)", "Límite Superior (B)", "Punto Medio (C)", "Error (Ea)", "F(A)", "F(B)", "F(C)"):
            self.tablaTrv.heading(col, text=col)
            self.tablaTrv.column(col, width=150, anchor='w')
        self.tablaTrv.pack(fill=tk.BOTH, expand=True)

        # GRAFICADOR
        self.grafica = ttk.Frame(self.ventanaPrincipal_AN, padding=8)
        self.grafica.pack(side=tk.TOP, fill=tk.BOTH)

    def resolverEcuacion(self):
        metodo_num = self.metodosCerrados.get()

        if metodo_num == 'Método de bisección':
            try:
                lim_inferior = float(self.limI.get().strip())
                lim_superior = float(self.limS.get().strip())
                func = self.ecuacion.get().strip()

                self.tablaTrv.delete(*self.tablaTrv.get_children())

                resultados = metodoBiseccion(lim_inferior, lim_superior, func)
                for fila in resultados:
                    self.tablaTrv.insert("", tk.END, values=fila)

            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {e}")

        elif metodo_num == 'Método de falsa posición':
            try:
                self.tablaTrv.delete(*self.tablaTrv.get_children())

                # Ingresar algoritmo para metodo de Falsa Posición aquí

            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def graficarFuncion(self):

        for e in self.grafica.winfo_children():
            e.destroy()

        ecua = self.ecuacion.get().strip()
        ecua = ecua.replace("^", "**")

        ecua = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', ecua)
        
        try:
            ejeX = numpy.linspace(-10, 10, 40)
        
            # Crear un entorno seguro para evaluar la función
            # Permitimos las funciones matemáticas comunes
            entorno = {name: getattr(numpy, name) for name in dir(numpy) if not name.startswith("_")}
            entorno.update({"x": ejeX, "pi": numpy.pi, "e": numpy.e})

            ejeY = eval(ecua, {"__builtins__": None}, entorno)
            # Crear figura
            fig = Figure(figsize=(4, 6), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(ejeX, ejeY, color="blue")
            # --- CONFIGURAR COMO PLANO CARTESIANO ---
            ax.spines["top"].set_color("none")      # Quita borde superior
            ax.spines["right"].set_color("none")    # Quita borde derecho
            ax.spines["left"].set_position("zero")  # Eje Y pasa por x=0
            ax.spines["bottom"].set_position("zero")# Eje X pasa por y=0

            ax.set_aspect("auto")                   # Mantiene proporción libre
            ax.grid(True, linestyle="--", linewidth=0.1)
            ax.set_title(f"Gráfica de y = {pretty(ecua)}", fontsize=12)

            # Mostrar en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.grafica)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        except:
            messagebox.showerror(title="Error a la hora de graficar", message="Algo salió mal a la hora de grafica la función")

    def _build_ui(self):
        # Selección de tipo de operación
        top = ttk.Frame(self.ventanaPrincipal, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        # Botones
        ttk.Button(top, text="Generar entradas", command=self.generar_entradas, style='Accent.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Resolver / Ejecutar", command=self.resolver, style='Accent.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Limpiar", command=self.limpiar, style='Accent.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Volver al menú", command=lambda: [self.ventanaPrincipal.wm_withdraw(), self.menuPrincipal.wm_deiconify()], style='Accent.TButton').pack(side=tk.RIGHT, padx=6)


        paned = ttk.Panedwindow(self.ventanaPrincipal, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Izquierda: Crear siete botones de manera vertical que reemplacen las acciones del raddiobutton
        izquierda = ttk.Frame(paned, width=420)
        paned.add(izquierda, weight=0)
        ttk.Button(izquierda, text="Sistemas", width=25, style='Accent.TButton', command=lambda: [self.metodo.set('sistemas'), self._on_method_change()]).pack(fill=tk.X, padx=2, pady=(0,30))
        ttk.Button(izquierda, text="Suma", width=25, style='Accent.TButton', command=lambda: [self.metodo.set('suma'), self._on_method_change()]).pack(fill=tk.X, padx=2, pady=30)
        ttk.Button(izquierda, text="Multiplicación", width=25, style='Accent.TButton', command=lambda: [self.metodo.set('multiplicacion'), self._on_method_change()]).pack(fill=tk.X, padx=2, pady=30)
        ttk.Button(izquierda, text="Transpuesta", width=25, style='Accent.TButton', command=lambda: [self.metodo.set('transpuesta'), self._on_method_change()]).pack(fill=tk.X, padx=2, pady=30)
        ttk.Button(izquierda, text="Independencia Lineal", width=25, style='Accent.TButton', command=lambda: [self.metodo.set('independencia'), self._on_method_change()]).pack(fill=tk.X, padx=2, pady=30)
        ttk.Button(izquierda, text="Inversa", width=25, style='Accent.TButton', command=lambda: [self.metodo.set('inversa'), self._on_method_change()]).pack(fill=tk.X, padx=2, pady=30)
        ttk.Button(izquierda, text="Determinante", width=25, style='Accent.TButton', command=lambda: [self.metodo.set('det'), self._on_method_change()]).pack(fill=tk.X, padx=2, pady=30)

        # Barras de desplazamiento para las entradas
        centro = ttk.Frame(paned, width=420)
        paned.add(centro, weight=0)

        self.canvas = tk.Canvas(centro)
        self.canvas.configure(background='#0b5c71')
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        vbar = ttk.Scrollbar(centro, orient=tk.VERTICAL, command=self.canvas.yview)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=vbar.set)
        self.entradas_contenedor = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.entradas_contenedor, anchor='nw')
        self.entradas_contenedor.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Derecha: El log y la pantalla de resultados
        derecha = ttk.Frame(paned, width=420)
        paned.add(derecha, weight=0)
        ttk.Label(derecha, text="Registro (paso a paso):", font=(None,10,'bold'), background='#0b5c71', foreground='#e6e6e6').pack(anchor='w')
        # Log con fuente monoespaciada y fondo blanco para legibilidad
        self.log_texto = tk.Text(derecha, height=24, state='disabled', bg='#ffffff', font=('Consolas', 10), padx=6, pady=6)
        self.log_texto.pack(fill=tk.BOTH, expand=True)
        log_scroll = ttk.Scrollbar(derecha, orient=tk.VERTICAL, command=self.log_texto.yview)
        log_scroll.place(relx=1.0, rely=0, relheight=1.0, anchor='ne')
        self.log_texto.configure(yscrollcommand=log_scroll.set)

        ttk.Label(derecha, text="Resultado / Soluciones:", font=(None,10,'bold'), background='#0b5c71', foreground='#e6e6e6').pack(anchor='w', pady=(6,0))
        self.result_var = tk.StringVar(value='-')
        # Caja de resultado con fondo blanco y relieve para destacarla
        result_box = tk.Label(derecha, textvariable=self.result_var, bg='white', relief='sunken', padx=8, pady=6, font=('Segoe UI', 10))
        result_box.pack(fill=tk.X)

        # inicial
        self._on_method_change()

    def _on_method_change(self):
        metodo = self.metodo.get()

        # Limpiar la zona de entradas y generar instrucciones
        for w in self.entradas_contenedor.winfo_children():
            w.destroy()

        ttk.Label(self.entradas_contenedor, text="Instrucciones de Entrada:\n", font=('Helvetica',12,'bold')).pack(anchor='w', pady=(0,6))

        cuadro_marco = ttk.Frame(self.entradas_contenedor)
        cuadro_marco.pack(anchor='w')

        # Si la operación solo necesita una matriz
        def fils_col():
            ttk.Label(cuadro_marco, text="Filas (n):").grid(row=0, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
            ttk.Label(cuadro_marco, text="Columnas (m):").grid(row=1, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_var_var, width=6).grid(row=1, column=1, padx=4)

        # Si la operación utiliza dos matrices
        def a_b():
            # Cambio de mensaje si es suma
            if metodo == 'suma':
                ttk.Label(cuadro_marco, text="Filas: ").grid(row=0, column=0)
            else:
                ttk.Label(cuadro_marco, text="A => Filas: ").grid(row=0, column=0)
            ttk.Entry(cuadro_marco, textvariable=self.matA_filas, width=4).grid(row=0, column=1)
            ttk.Label(cuadro_marco, text=" , Columnas: ").grid(row=0, column=2)
            ttk.Entry(cuadro_marco, textvariable=self.matA_columnas, width=4).grid(row=0, column=3)
            # Cambio de ubicación de escalar si es suma
            if metodo == 'suma':
                ttk.Label(cuadro_marco, text=" Escalar para A: ").grid(row=1, column=0)
                ttk.Entry(cuadro_marco, textvariable=self.matA_escalar, width=4).grid(row=1, column=1)
            else:
                ttk.Label(cuadro_marco, text=" Escalar para A: ").grid(row=0, column=4)
                ttk.Entry(cuadro_marco, textvariable=self.matA_escalar, width=4).grid(row=0, column=5)
            # Ingreso de valores para B si es multiplicación
            if metodo == 'multiplicacion':                
                ttk.Label(cuadro_marco, text="B => Filas: ").grid(row=1, column=0)
                ttk.Entry(cuadro_marco, textvariable=self.matB_filas, width=4).grid(row=1, column=1)
                ttk.Label(cuadro_marco, text=" , Columnas: ").grid(row=1, column=2)
                ttk.Entry(cuadro_marco, textvariable=self.matB_columnas, width=4).grid(row=1, column=3)
            # Cambio de ubicación de escalar si es suma
            if metodo == 'suma':
                ttk.Label(cuadro_marco, text=" , Escalar para B: ").grid(row=1, column=2)
                ttk.Entry(cuadro_marco, textvariable=self.matB_escalar, width=4).grid(row=1, column=3)
            else:
                ttk.Label(cuadro_marco, text=" Escalar para B: ").grid(row=1, column=4)
                ttk.Entry(cuadro_marco, textvariable=self.matB_escalar, width=4).grid(row=1, column=5)

        if metodo == 'sistemas':
            ttk.Label(self.entradas_contenedor, text="1. Seleccione el método para resolver el sistema de ecuaciones.").pack(anchor='w')
            self.opciones = ttk.Combobox(self.entradas_contenedor, textvariable=self.metodoEscoger, values=('Gauss-Jordan','Gauss','Regla de Cramer'))
            self.opciones.pack(anchor='w')
            self.opciones.state(["readonly"])

            ttk.Label(self.entradas_contenedor, text="2. Ingrese el número de ecuaciones del sistema").pack(anchor='w')
            ttk.Label(cuadro_marco, text="N° de ecuaciones:").grid(row=0, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
            ttk.Label(self.entradas_contenedor, text="3. Genere los cuadros de entradas, y en cada uno,\ningrese la ecuación").pack(anchor='w')
            ttk.Label(self.entradas_contenedor, text="4. Una vez ingresadas las ecuaciones, si desea, haga clic en \n'Ecuación Matricial'. Si no, haga clic en 'Resolver'").pack(anchor='w')

            # Una pequeña nota al usuario, sobre cómo debe ingresar cada ecuación
            ttk.Label(self.entradas_contenedor, text="Nota: Para las incógnitas, escribalas como x1, x2, x3 y así\nsucesivamente.").pack(anchor='w')


        elif metodo == 'suma':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas de las dos matrices.").pack(anchor='w')
            a_b()
            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de las matrices.\n3. Digite los valores de cada matriz.").pack(anchor='w')
            ttk.Label(self.entradas_contenedor, text="(Si no se especifica la escalar para alguna de las matrices,\n entonces la escalar para dicha matriz será 1)").pack(anchor='w')

        elif metodo == 'multiplicacion':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas para las matrices A y B.").pack(anchor='w')
            a_b()
            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas para ambas matrices\n3. Digite los valores para cada matriz").pack(anchor='w')

        elif metodo in ('transpuesta', 'inversa', 'det'):
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas de la matriz inicial.").pack(anchor='w')
            fils_col()
            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de la matriz.\n3. Digite los valores de la matriz.").pack(anchor='w')

        elif metodo == 'independencia':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de vectores (columnas) y entradas (filas).").pack(anchor='w')
            fils_col()
            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de cada vector.\n3. Digite los valores de cada vector.").pack(anchor='w')

        else:
            ttk.Label(self.entradas_contenedor, text="Seleccione un método de operación.").pack(anchor='w')

    def generar_entradas(self):
        metodo = self.metodo.get()

        self.entradas_aug = []
        self.entradas_A = []
        self.entradas_B = []

        if metodo == 'sistemas':
            # generar matriz aumentada
            try:
                n = int(self.num_eq_var.get())
                if n <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror('Entrada inválida', 'N° de ecuaciones debe ser un número no negativo')
                return

            ttk.Label(self.entradas_contenedor,text="Sistema lineal:").pack(anchor='w')
            
            grid_e = ttk.Frame(self.entradas_contenedor)
            grid_e.pack(anchor='w')

            # entradas
            for i in range(n):
                filas_entrada = []

                ttk.Label(grid_e, text=f"Ec {i + 1}:", padding=5).grid(row=i, column=0, pady=2)
                
                e_b = ttk.Entry(grid_e, width=35)
                e_b.grid(row=i, column=1, padx=2)
                
                filas_entrada.append(e_b)

                self.entradas_aug.append(filas_entrada)

            # Botón para mostrar la equivalencia del sistema en forma matricial
            ttk.Button(grid_e, text='Forma Matricial', command=self.transformarSistema).grid(row= n + 1, column=1, pady=8)

        elif metodo == 'suma':

            try:
                r = int(self.matA_filas.get())
                c = int(self.matA_columnas.get())
                if r <= 0 or c <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror('Entrada inválida', 'Filas y columnas deben ser enteros positivos para A y B.')
                return

            ttk.Label(self.entradas_contenedor, text=f'Matriz A ({r}×{c})').pack(anchor='w')
            frameA = ttk.Frame(self.entradas_contenedor); frameA.pack(pady=4)
            for i in range(r):
                fila = []
                for j in range(c):
                    e = ttk.Entry(frameA, width=10)
                    e.grid(row=i, column=j, padx=2, pady=2)
                    fila.append(e)
                self.entradas_A.append(fila)

            ttk.Label(self.entradas_contenedor, text=f'Matriz B ({r}×{c})').pack(anchor='w')
            frameB = ttk.Frame(self.entradas_contenedor); frameB.pack(pady=4)
            for i in range(r):
                fila = []
                for j in range(c):
                    e = ttk.Entry(frameB, width=10)
                    e.grid(row=i, column=j, padx=2, pady=2)
                    fila.append(e)
                self.entradas_B.append(fila)

        elif metodo == 'multiplicacion':
            try:
                r = int(self.matA_filas.get())
                k = int(self.matA_columnas.get())
                k2 = int(self.matB_filas.get())
                c = int(self.matB_columnas.get())
                if r <= 0 or k <= 0 or k2 <= 0 or c <= 0:
                    raise ValueError
                if k != k2:
                    messagebox.showerror('Incompatibilidad', 'Columnas de A deben igualar filas de B para multiplicar.')
                    return
            except Exception:
                messagebox.showerror('Entrada inválida', 'Dimensiones deben ser enteros positivos y compatibles.')
                return

            ttk.Label(self.entradas_contenedor, text=f'Matriz A ({r}×{k})').pack(anchor='w')
            frameA = ttk.Frame(self.entradas_contenedor); frameA.pack(pady=4)
            for i in range(r):
                fila = []
                for j in range(k):
                    e = ttk.Entry(frameA, width=10)
                    e.grid(row=i, column=j, padx=2, pady=2)
                    fila.append(e)
                self.entradas_A.append(fila)

            ttk.Label(self.entradas_contenedor, text=f'Matriz B ({k}×{c})').pack(anchor='w')
            frameB = ttk.Frame(self.entradas_contenedor); frameB.pack(pady=4)
            for i in range(k):
                fila = []
                for j in range(c):
                    e = ttk.Entry(frameB, width=10)
                    e.grid(row=i, column=j, padx=2, pady=2)
                    fila.append(e)
                self.entradas_B.append(fila)
        elif metodo in ('transpuesta', 'inversa', 'det'):

            try:
                n = int(self.num_eq_var.get())
                m = int(self.num_var_var.get())
                if n <= 0 or m <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror('Entrada inválida', 'Filas y columnas deben ser enteros positivos.')
                return

            ttk.Label(self.entradas_contenedor, text=f'Matriz: {n} filas × {m} columnas').pack(anchor='w')
            grid = ttk.Frame(self.entradas_contenedor)
            grid.pack(pady=6)

            # entradas
            for i in range(n):
                filas_entrada = []
                for j in range(m):
                    e = ttk.Entry(grid, width=12)
                    e.grid(row=i+1, column=j, padx=2, pady=2)
                    filas_entrada.append(e)
                self.entradas_aug.append(filas_entrada)
        
        elif metodo == 'independencia':

            try:
                n = int(self.num_eq_var.get())
                m = int(self.num_var_var.get())
                if n <= 0 or m <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror('Entrada inválida', 'Filas y columnas deben ser enteros positivos.')
                return

            grid = ttk.Frame(self.entradas_contenedor)
            grid.pack(pady=6)
            # encabezados
            for j in range(m):
                ttk.Label(grid, text=f'v{j+1}', anchor='center', width=10).grid(row=0, column=j)
            # entradas
            for i in range(n):
                filas_entrada = []
                for j in range(m):
                    e = ttk.Entry(grid, width=12)
                    e.grid(row=i+1, column=j, padx=2, pady=2)
                    filas_entrada.append(e)
                self.entradas_aug.append(filas_entrada)

    def _leer_matriz(self, entradas):
        M = []

        for i, r in enumerate(entradas):
            fila = []
            for j, e in enumerate(r):
                val = e.get().strip()
                if val == '':
                    val = '0'
                try:
                    num = Fraction(val)
                except Exception:
                    raise ValueError(f"Valor inválido en fila {i + 1}, columna {j + 1}: '{val}'")
                fila.append(num)
            M.append(fila)

        return M
    
    def transformarSistema(self):

        numVars = []
        matrizEqv= []
        sistema = []
        
        self.log_texto.configure(state='normal')
        self.log_texto.delete('1.0', tk.END)
        self.log_texto.configure(state='disabled')
        
        text_redirector = _TextRedirector(self.log_texto)

        with redirect_stdout(text_redirector):
            
            print("A partir del sistema dado:\n")

            try:

                for i, ec in enumerate(self.entradas_aug):
                
                    matrizEqv.append(list())
                    sistema.append(list())
                
                    for r in ec:
            
                        u = r.get().strip()

                        # Insertar '*' entre número y variable (por ejemplo, 2x → 2*x)
                        u = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', u)
                    
                        # También entre variable y paréntesis (por ejemplo, x(y+1) → x*(y+1))
                        u = re.sub(r'([a-zA-Z])\(', r'\1*(', u)
                    
                        # Y entre paréntesis y variable ((x+1)y → (x+1)*y)
                        u = re.sub(r'\)([a-zA-Z])', r')*\1', u)

                        if not '=' in u: # Si no hay signo igual, tira un error

                            messagebox.showerror(title=f"Error en la ecuación {i + 1}", message="Falta el signo '='")
                        elif len(u.split('=')) > 2: # Si en la ecuación, hay un '=' de más, se lanza un error

                            messagebox.showerror(title=f"Error en la ecuación {i + 1}", message="Ingresó de manera érronea la ecuación")
                        else:

                            # A partir del signo '=', se divide la ecuación en dos partes
                            ladoIzquierdo, ladoDerecho = u.split('=')
                        
                            ladoIzquierdo = sympify(ladoIzquierdo)
                            ladoDerecho = sympify(ladoDerecho)

                            vars_ladoDerecho = list(ladoDerecho.free_symbols)

                            # Si en el lado derecho, hay términos, esos términos se transponen al lado izquierdo
                            if vars_ladoDerecho != []:

                                for var in vars_ladoDerecho:

                                    ladoIzquierdo -= ladoDerecho.coeff(var)*var
                                    ladoDerecho -= ladoDerecho.coeff(var)*var # Se quitan los términos del lado derecho

                            # Se obtiene los términos usados en la fila
                            terminos = sorted(list(ladoIzquierdo.free_symbols), key=lambda x: str(x), reverse=True)
                            numVars.append(terminos[0])

                            # Se imprimen las ecuaciones respectivamente
                            print(f"{pretty(ladoIzquierdo)} = {ladoDerecho}")

                            sistema[i].append(ladoIzquierdo)
                            sistema[i].append(ladoDerecho)

                numVars = sorted(list(numVars), key=lambda x: str(x), reverse=True)
                numVars[0] = str(numVars[0])

                # Se calcula el número de columnas que tiene el sistema
                numCol = int(numVars[0].replace('x',''))

                # Lista que genera variables del tipo 'x1', 'x2', 'x3', etc
                # Se utiliza para verificar si el usuario escribió las incógnitas de esa manera
                incognitas = list(symbols(f'x1:{numCol + 1}'))
                
                for p in range(len(self.entradas_aug)):

                    for q in range(numCol):

                        # Agrega los coeficientes de las incógnitas
                        matrizEqv[p].append(sistema[p][0].coeff(incognitas[q]))

                    # Se agrega el término independiente de la respectiva fila
                    matrizEqv[p].append(sistema[p][1])
        
                print("\nEl sistema, en forma matricial, sería de la siguiente manera:\n")
                imprimir_matriz(matrizEqv)

                # Retorna el resultado, el cual es usado para su resolución
                return matrizEqv
            except: # Lanza una excepción por si algo sale mal a la hora de transformar el sistema en forma matricial

                messagebox.showerror(title="Error fatal", message="Algo salió mal a la hora de leer el sistema. " \
                "Revise si escribió de forma correcta el sistema", icon="warning")

    def resolver(self):
        metodo = self.metodo.get()
        # limpiar log
        self.log_texto.configure(state='normal')
        self.log_texto.delete('1.0', tk.END)
        self.log_texto.configure(state='disabled')
        self.result_var.set('Procesando...')

        # redirige cualquier print que se puede hacer
        text_redirector = _TextRedirector(self.log_texto)

        try:
            # redirigir cualquier print al Text (para mostrar pasos)
            with redirect_stdout(text_redirector):
                if metodo == 'sistemas':
                    
                    if not self.entradas_aug:
                        raise ValueError('Primero genere la matriz aumentada (botón "Generar entradas").')
                    
                    matriz = self.transformarSistema()

                    opcion = self.opciones.get()

                    match (opcion):

                        case "Gauss-Jordan":

                            eliminacionGaussJordan(matriz)
                            self.result_var.set("La matriz se redujo a la forma escalonada reducida")
                        case "Gauss":

                            eliminacionGauss(matriz)
                            self.result_var.set("La matriz se redujo a la forma escalonada")
                        case "Regla de Cramer":

                            reglaCramer(matriz)
                            self.result_var.set("Se encontraron las soluciones del sistema")
                        case _:

                            raise ValueError('Primero, elija un método para resolver el sistema')
                    
                elif metodo == 'suma':
                    if not self.entradas_A or not self.entradas_B:
                        raise ValueError('Genere las entradas de A y B primero.')
                    A = self._leer_matriz(self.entradas_A)

                    # Si no se define una escalar, entonces se dice que es '1'
                    if self.matA_escalar.get().strip() == '' or self.matA_escalar.get().strip() == '1':

                        escalarA = 1
                    else:

                        try:

                            escalarA = Fraction(self.matA_escalar.get().strip())
                        except:

                            print("En la matriz A, ingresó una escalar no válida")
                    
                    B = self._leer_matriz(self.entradas_B)

                    # Si no se define una escalar, entonces se dice que es '1'
                    if self.matB_escalar.get().strip() == '' or self.matB_escalar.get().strip() == '1':

                        escalarB = 1
                    else:

                        try:

                            escalarB = Fraction(self.matB_escalar.get().strip())
                        except:

                            print("En la matriz B, ingresó una escalar no válida")

                    suma_matrices(A, B, escalarA, escalarB)
                    self.result_var.set("Suma realizada — ver registro")

                elif metodo == 'multiplicacion':
                    if not self.entradas_A or not self.entradas_B:
                        raise ValueError('Genere las entradas de A y B primero.')
                    
                    A = self._leer_matriz(self.entradas_A)

                    if self.matA_escalar.get().strip() == '' or self.matA_escalar.get().strip() == '1':

                        escalarA = 1
                    else:

                        try:

                            escalarA = Fraction(self.matA_escalar.get().strip())
                        except:

                            print("En la matriz A, ingresó una escalar no válida")

                    # Si no se define una escalar, entonces se dice que es '1'
                    if self.matB_escalar.get().strip() == '' or self.matB_escalar.get().strip() == '1':

                        escalarB = 1
                    else:

                        try:

                            escalarB = Fraction(self.matB_escalar.get().strip())
                        except:

                            print("En la matriz B, ingresó una escalar no válida")

                    
                    B = self._leer_matriz(self.entradas_B)
                    multiplicar_matrices(A, B, escalarA, escalarB)
                    self.result_var.set("Multiplicación realizada — ver registro")
                elif metodo == 'transpuesta':

                    if not self.entradas_aug:
                        raise ValueError('Primero genere la matriz (botón "Generar entradas").')
                    
                    matriz = self._leer_matriz(self.entradas_aug)
                    transpuestamatriz(matriz)

                    self.result_var.set("Este es el resultado de la transpuesta")

                elif metodo == 'independencia':

                    if not self.entradas_aug:
                        raise ValueError('Primero genere el conjunto de vectores (botón "Generar entradas").')
                    
                    matriz = self._leer_matriz(self.entradas_aug)
                    independenciaLineal(matriz)

                    self.result_var.set("La operación ya fue realizada")

                elif metodo == 'inversa':
                    
                    if not self.entradas_aug:
                        raise ValueError('Primero genere la matriz (botón "Generar entradas").')
                    
                    matriz = self._leer_matriz(self.entradas_aug)

                    inversaMatriz(matriz)
                    self.result_var.set("Se encontró con éxito la inversa de la matriz")

                elif metodo == 'det':
                    
                    if not self.entradas_aug:
                        raise ValueError('Primero genere la matriz (botón "Generar entradas").')
                    
                    matriz = self._leer_matriz(self.entradas_aug)
                    
                    print("Primero, se aplica eliminación de Gauss, para reducirla a la matriz triangular superior")
                    print("Para calcular la determinante, se multiplica cada elemento de la diagonal principal")
                    print("Si hay un cero, entonces la determinante es 0")

                    detMatriz(matriz)
                    self.result_var.set("Se encontró con éxito la determinante de la matriz")

        except Exception as exc:
            # Mostrar la traza de error en log y un messagebox
            import traceback
            tb = traceback.format_exc()
            self.log_texto.configure(state='normal')
            self.log_texto.insert(tk.END, "ERROR:\n" + tb)
            self.log_texto.configure(state='disabled')
            messagebox.showerror('Error', str(exc))
            self.result_var.set('-')
            return

    def limpiar(self):
        for w in self.entradas_contenedor.winfo_children():
            w.destroy()
        self.entradas_aug = []
        self.entradas_A = []
        self.entradas_B = []
        self.log_texto.configure(state='normal')
        self.log_texto.delete('1.0', tk.END)
        self.log_texto.configure(state='disabled')
        self.result_var.set('-')

    def _guardar_log(self):
        contenido = ''
        try:
            self.log_texto.configure(state='normal')
            contenido = self.log_texto.get('1.0', tk.END)
            self.log_texto.configure(state='disabled')
        except Exception:
            pass
        if not contenido.strip():
            messagebox.showinfo('Guardar log', 'No hay contenido en el registro para guardar.')
            return
        fname = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files','*.txt')])
        if fname:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(contenido)
            messagebox.showinfo('Guardar log', f'Registro guardado en: {fname}')

    def run(self):
        
        self.menuPrincipal.mainloop()