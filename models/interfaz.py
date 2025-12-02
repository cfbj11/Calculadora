# models/interfaz.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
from contextlib import redirect_stdout
from sympy import sympify, symbols, pretty, Symbol, lambdify, diff, simplify
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy
import customtkinter as ctk

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
from models.reglaFalsa import reglaFalsa
from models.newtonRaphson import metodoNewton
from models.secante import metodoSecante

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

        self.maximizarVentana(self.menuPrincipal)

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
            self.menuPrincipal.configure(background="#a6cfd9")
        except Exception:
            pass
        
        ctk.CTkLabel(self.menuPrincipal, text="NumExpert", font=('Bahnschrift SemiBold', 72, 'bold'), text_color='#000000').pack(anchor='center', pady=100)
        ctk.CTkLabel(self.menuPrincipal, text="Seleccione una opción", font=('Times New Roman', 48), text_color='#000000').pack(anchor='center', pady=40)

        ctk.CTkButton(self.menuPrincipal, text="Álgebra Lineal", font=('Georgia', 32, 'bold'), width=225, height=75, text_color='#000000',command=lambda: [self.menuPrincipal.wm_withdraw(), self.algebraLineal()], fg_color="#20b1aa").pack(anchor='center', pady=20)
        ctk.CTkButton(self.menuPrincipal, text="Análisis Númerico", font=('Georgia', 32, 'bold'), width=225, height=75, text_color='#000000', command=lambda: [self.menuPrincipal.wm_withdraw(), self.analisisNumerico()], fg_color="#20b1aa").pack(anchor='center', pady=10)

        ctk.CTkLabel(self.menuPrincipal, text="© Copyright 2025 - 2025", font=('Times New Roman', 28), text_color='#000000').pack(anchor='s', pady=15)
    
    def maximizarVentana(self, ventana):

        try:
            ventana.state('zoomed')
        except Exception:
            try:
                ventana.attributes('-zoomed', True)
            except Exception:
                # No se pudo maximizar automáticamente; se mantiene la geometría por defecto
                pass
    
    def algebraLineal(self):
        self.ventanaPrincipal = Toplevel(self.menuPrincipal)
        self.ventanaPrincipal.title("NumExpert (Álgebra Lineal)")
        self.ventanaPrincipal.geometry("1350x720")
        self.ventanaPrincipal.configure(background='#0b5c71')
        
        self.maximizarVentana(self.ventanaPrincipal)

        # Al cerrar esta subventana desde el decorador (X), cerrar la app completamente
        self.ventanaPrincipal.protocol("WM_DELETE_WINDOW", lambda: self._close_from_subwindow(self.ventanaPrincipal))

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
        self.ventanaPrincipal_AN.configure(background='#0b5c71')

        self.maximizarVentana(self.ventanaPrincipal_AN)

        # Al cerrar esta subventana desde el decorador (X), cerrar la app completamente
        self.ventanaPrincipal_AN.protocol("WM_DELETE_WINDOW", lambda: self._close_from_subwindow(self.ventanaPrincipal_AN))

        # Configuración de estilos (tema y apariencia)
        # Usamos ttk.Style para aplicar una apariencia más moderna y coherente
        style = ttk.Style(self.menuPrincipal)
        try:
            # 'clam' suele permitir más personalización en Windows y Linux
            style.theme_use('clam')
        except Exception:
            pass

        # VARIABLES
        self.tipo_metnum = tk.StringVar(value="met_cerr")
        self.metodoNum = tk.StringVar(value="(Elige un método)")
        self.ecuacionEntrada = tk.StringVar(value="")
        self.limInf = tk.StringVar(value="")
        self.limSup = tk.StringVar(value="")
        self.tolerancia = tk.StringVar(value="0.00001")

        metodos = ttk.Frame(self.ventanaPrincipal_AN)
        metodos.pack(side='top', fill='x')

        # BOTONES DE LA PARTE SUPERIOR
        ctk.CTkButton(metodos, text="Métodos Cerrados", font=('Georgia', 16, 'bold'), height=30, fg_color='#e6e6e6', text_color='#3b8b87', command=lambda:(self.tipo_metnum.set('met_cerr'), self.tipo_met(), self.metodoCerrado())).pack(side='left', padx=5, pady=5)
        ctk.CTkButton(metodos, text="Métodos Abiertos", font=('Georgia', 16, 'bold'), height=30, fg_color='#e6e6e6', text_color='#3b8b87', command=lambda:(self.tipo_metnum.set('met_abier'), self.tipo_met(), self.metodoAbierto())).pack(side='left', padx=5, pady=5)

        ctk.CTkButton(metodos, text="Volver al menú", font=('Georgia', 16, 'bold'), height=30, fg_color='#e6e6e6', text_color="#ff0000", command=lambda: [self.ventanaPrincipal_AN.wm_withdraw(), self.menuPrincipal.wm_deiconify(), self.maximizarVentana(self.menuPrincipal)]).pack(side='right', padx=5, pady=5)

        self.izquierda = ctk.CTkFrame(self.ventanaPrincipal_AN, fg_color='#0b5c71')
        self.izquierda.pack(side='left', fill='y', padx=5, pady=5)

        # RESULTADO NUMÉRICO
        self.respuestaNum = ttk.Frame(self.ventanaPrincipal_AN, height=30)
        self.respuestaNum.pack(side='top', fill='both')

        # PROCEDIMIENTO Y RESULTADOS
        self.procedimiento = ctk.CTkFrame(self.ventanaPrincipal_AN, fg_color='#0b5c71')
        self.procedimiento.pack(side='top', fill='both', expand=True, padx=5, pady=5)

        # GRAFICADOR
        self.grafica = ttk.Frame(self.ventanaPrincipal_AN, padding=8)
        self.grafica.pack(side='top', fill='both')

        self.metodoCerrado()

    def metodoCerrado(self):

        for w in self.izquierda.winfo_children():

            w.destroy()

        for w in self.procedimiento.winfo_children():

            w.destroy()
        
        self.superindices = {"0": "⁰","1": "¹","2": "²","3": "³","4": "⁴","5": "⁵","6": "⁶","7": "⁷","8": "⁸","9": "⁹", "x":"ˣ"}

        def procesar(evento):
            texto = self.ecuacion.get()
            if "^" in texto:
                nuevo = ""
                i = 0
                while i < len(texto):
                    if texto[i] == "^" and i + 1 < len(texto):
                        sig = texto[i+1]
                        if sig in self.superindices:
                            nuevo += self.superindices[sig]
                            i += 2
                            continue
                    nuevo += texto[i]
                    i += 1
                self.ecuacion.delete(0, tk.END)
                self.ecuacion.insert(0, nuevo)
        
        ttk.Label(self.izquierda, text="Ingrese la ecuación:", font=('Georgia', 14, 'bold')).grid(row=0,column=0,pady=5, padx=5)
        self.ecuacion = ttk.Entry(self.izquierda, width=15, font=('Helvetica', 16, 'normal'))
        self.ecuacion.grid(row=1,column=0,pady=10)
        self.ecuacion.bind('<KeyRelease>', procesar)

        ctk.CTkButton(self.izquierda, text="Graficar función", font=('Georgia', 12, 'bold'), command=self.graficarFuncion, fg_color='#3b8b87').grid(row=2,column=0,pady=5, padx=5)

        ttk.Label(self.izquierda, text="Método para resolver la ecuación", font=('Georgia', 12, 'bold')).grid(row=3,column=0, pady=10)

        self.tipo_met()

        # Botones para mejorar la escritura de la ecuación
        botonesEcuacion = ctk.CTkFrame(self.izquierda, fg_color='#0b5c71')
        botonesEcuacion.grid(row=5,column=0)

        def insert(texto):
            pos = self.ecuacion.index(tk.INSERT)
            self.ecuacion.insert(pos, texto)

        botones = [
            ("^", "^"), ("e","e"), ("π","π"),
            ("sin(x)", "sin(x)"), ("cos(x)","cos(x)"), ("tan(x)","tan(x)"),
            ("csc(x)", "csc(x)"), ("sec(x)","sec(x)"), ("cot(x)","cot(x)"),
            ("asin(x)", "asin(x)"), ("acos(x)","acos(x)"), ("atan(x)","atan(x)"),
            ("log(x)", "log(x)"), ("ln(x)","ln(x)"), ("√","√()")
        ]

        fila = col = 0
        for txt, val in botones:
            ctk.CTkButton(botonesEcuacion, text=txt, font=(None, 14, 'bold'), command=lambda v=val:insert(v), width=70, fg_color="#FFFFFF", text_color="#000000").grid(row=fila, column=col, padx=5, pady=5)

            col += 1
            # Se reinicia el bucle y pasa a la siguiente fila
            if col == 3:
                col = 0
                fila += 1

        # ENTRADAS DEL INTERVALO
        self.intervaloRaiz = ctk.CTkFrame(self.izquierda, fg_color='#0b5c71')
        self.intervaloRaiz.grid(row=6,column=0)

        ttk.Label(self.intervaloRaiz, text="Intervalo (a partir de la gráfica)", font=('Georgia', 12, 'bold')).pack(anchor='center', pady=(30,10))
        
        ttk.Label(self.intervaloRaiz, text="Límite Inferior (A)", font=('Georgia', 12, 'bold')).pack(anchor='center', pady=4)
        self.limI = ttk.Entry(self.intervaloRaiz, width=13)
        self.limI.pack(anchor='center', pady=5)

        ttk.Label(self.intervaloRaiz, text="Límite Superior (B)", font=('Georgia', 12, 'bold')).pack(anchor='center', pady=4)
        self.limS = ttk.Entry(self.intervaloRaiz, width=13)
        self.limS.pack(anchor='center', pady=5)

        ttk.Label(self.intervaloRaiz, text="Tolerancia", font=('Georgia', 12, 'bold')).pack(anchor='center', pady=4)
        self.tol = ttk.Entry(self.intervaloRaiz, textvariable=self.tolerancia, width=13)
        self.tol.pack(anchor='center', pady=5)

        ctk.CTkButton(self.intervaloRaiz, text="Encontrar Respuesta", font=('Georgia', 12, 'bold'), command=self.resolverEcuacion, fg_color='#3b8b87').pack(anchor='center', pady=10)

        ttk.Label(self.procedimiento, text="RESULTADOS:", font=('Georgia',12,'bold'), background='#0b5c71', foreground='#e6e6e6').pack(anchor='w')

        # TABLA TREEVIEW
        self.tablaTrv = ttk.Treeview(self.procedimiento, columns=("#", "Límite Inferior (A)", "Límite Superior (B)", "C", "Error Absoluto", "F(A)", "F(B)", "F(C)"), show='headings')
        self.tablaTrv.pack(fill='both', expand=True)

        for col in ("#", "Límite Inferior (A)", "Límite Superior (B)", "C", "Error Absoluto", "F(A)", "F(B)", "F(C)"):
            if col == "#":
                self.tablaTrv.heading("#", text="#")
                self.tablaTrv.column("#", width=40, anchor='center')
            else:
                self.tablaTrv.heading(col, text=col)
                self.tablaTrv.column(col, width=150, anchor='w')
    
    def metodoAbierto(self):

        for w in self.izquierda.winfo_children():

            w.destroy()

        for w in self.procedimiento.winfo_children():

            w.destroy()

            self.superindices = {"0": "⁰","1": "¹","2": "²","3": "³","4": "⁴","5": "⁵","6": "⁶","7": "⁷","8": "⁸","9": "⁹", "x":"ˣ"}

        def procesar(evento):
            texto = self.ecuacion.get()
            if "^" in texto:
                nuevo = ""
                i = 0
                while i < len(texto):
                    if texto[i] == "^" and i + 1 < len(texto):
                        sig = texto[i+1]
                        if sig in self.superindices:
                            nuevo += self.superindices[sig]
                            i += 2
                            continue
                    nuevo += texto[i]
                    i += 1
                self.ecuacion.delete(0, tk.END)
                self.ecuacion.insert(0, nuevo)
        
        ttk.Label(self.izquierda, text="Ingrese la ecuación:", font=('Georgia', 14, 'bold')).grid(row=0,column=0,pady=5, padx=5)
        self.ecuacion = ttk.Entry(self.izquierda, width=15, font=('Helvetica', 16, 'normal'))
        self.ecuacion.grid(row=1,column=0,pady=10)
        self.ecuacion.bind('<KeyRelease>', procesar)

        ctk.CTkButton(self.izquierda, text="Graficar función", font=('Georgia', 12, 'bold'), command=self.graficarFuncion, fg_color='#3b8b87').grid(row=2,column=0,pady=5, padx=5)
        
        ttk.Label(self.izquierda, text="Método para resolver la ecuación", font=('Georgia', 12, 'bold')).grid(row=3,column=0, pady=10)
        
        self.tipo_met()

        # Botones para mejorar la escritura de la ecuación
        botonesEcuacion = ctk.CTkFrame(self.izquierda, fg_color='#0b5c71')
        botonesEcuacion.grid(row=5,column=0)

        def insert(texto):
            pos = self.ecuacion.index(tk.INSERT)
            self.ecuacion.insert(pos, texto)

        botones = [
            ("^", "^"), ("e","e"), ("π","π"),
            ("sin(x)", "sin(x)"), ("cos(x)","cos(x)"), ("tan(x)","tan(x)"),
            ("csc(x)", "csc(x)"), ("sec(x)","sec(x)"), ("cot(x)","cot(x)"),
            ("asin(x)", "asin(x)"), ("acos(x)","acos(x)"), ("atan(x)","atan(x)"),
            ("log(x)", "log(x)"), ("ln(x)","ln(x)"), ("√","√()")
        ]

        fila = col = 0
        for txt, val in botones:
            ctk.CTkButton(botonesEcuacion, text=txt, font=(None, 14, 'bold'), command=lambda v=val:insert(v), width=70, fg_color="#FFFFFF", text_color="#000000").grid(row=fila, column=col, padx=5, pady=5)

            col += 1
            # Se reinicia el bucle y pasa a la siguiente fila
            if col == 3:
                col = 0
                fila += 1
        # ENTRADAS PARA EL VALOR INICIAL
        self.valorIni = ctk.CTkFrame(self.izquierda, fg_color='#0b5c71')
        self.valorIni.grid(row=6,column=0)

        ttk.Label(self.valorIni, text="Valor Inicial", font=('Georgia', 12, 'bold')).pack(anchor='center', pady=4)
        self.val_I = ttk.Entry(self.valorIni, width=13)
        self.val_I.pack(anchor='center', pady=5)

        ttk.Label(self.valorIni, text="Tolerancia", font=('Georgia', 12, 'bold')).pack(anchor='center', pady=4)
        self.tol = ttk.Entry(self.valorIni, textvariable=self.tolerancia, width=13)
        self.tol.pack(anchor='center', pady=5)

        ctk.CTkButton(self.valorIni, text="Encontrar Respuesta", font=('Georgia', 12, 'bold'), command=self.resolverEcuacion, fg_color='#3b8b87').pack(anchor='center', pady=10)

        ttk.Label(self.procedimiento, text="RESULTADOS:", font=('Georgia',12,'bold'), background='#0b5c71', foreground='#e6e6e6').pack(anchor='w')

        # TABLA TREEVIEW
        self.tablaTrv = ttk.Treeview(self.procedimiento, columns=("#", "xi (Valor Inicial)", "xi + 1", "Error Absoluto", "F(xi)", "F'(xi)"), show='headings')
        self.tablaTrv.pack(fill='both', expand=True)

        for col in ("#", "xi (Valor Inicial)", "xi + 1", "Error Absoluto", "F(xi)", "F'(xi)"):
            if col == "#":
                self.tablaTrv.heading("#", text="#")
                self.tablaTrv.column("#", width=40, anchor='center')
            else:
                self.tablaTrv.heading(col, text=col)
                self.tablaTrv.column(col, width=150, anchor='w')

    def tipo_met(self):
        tipo = self.tipo_metnum.get()
        
        # Borrar lista si existe
        for w in self.izquierda.grid_slaves(row=4, column=0):
            w.destroy()
            self.metodoNum = tk.StringVar(value="(Elige un método)")

        if tipo == 'met_cerr':
            self.metodosCerrados = ctk.CTkComboBox(self.izquierda, variable=self.metodoNum, width=250, values=('Método de Bisección', 'Método de Falsa Posición'), state='readonly', font=('Helvetica', 14, 'bold'))
            self.metodosCerrados.grid(row=4, column=0, pady=5)
        elif tipo == 'met_abier':
            self.metodosAbiertos = ctk.CTkComboBox(self.izquierda, variable=self.metodoNum, width=250, values=('Método de Newton-Raphson', 'Método de la Secante'), state='readonly', font=('Helvetica', 14, 'bold'), command=self.tablasMetodosAbiertos)
            self.metodosAbiertos.grid(row=4, column=0, pady=5)
    
    def tablasMetodosAbiertos(self, tipo):

        for p in self.procedimiento.winfo_children():

            p.destroy()

        ttk.Label(self.procedimiento, text="RESULTADOS:", font=(None,12,'bold'), background='#0b5c71', foreground='#e6e6e6').pack(anchor='w')
        
        for b in self.valorIni.winfo_children():

            b.destroy()
        
        if tipo == "Método de Newton-Raphson":

            ttk.Label(self.valorIni, text="Valor Inicial (xi)", font=(None, 11, 'bold')).pack(anchor='center', pady=4)
            self.val_I = ttk.Entry(self.valorIni, width=13)
            self.val_I.pack(anchor='center', pady=5)

            ttk.Label(self.valorIni, text="Tolerancia", font=(None, 11, 'bold')).pack(anchor='center', pady=4)
            self.tol = ttk.Entry(self.valorIni, textvariable=self.tolerancia, width=13)
            self.tol.pack(anchor='center', pady=5)

            ctk.CTkButton(self.valorIni, text="Encontrar Respuesta", command=self.resolverEcuacion, fg_color='#3b8b87').pack(anchor='center', pady=10)
            
            # TABLA TREEVIEW
            self.tablaTrv = ttk.Treeview(self.procedimiento, columns=("#", "xi (Valor Inicial)", "xi + 1", "Error Absoluto", "F(xi)", "F'(xi)"), show='headings')
            self.tablaTrv.pack(fill='both', expand=True)

            for col in ("#", "xi (Valor Inicial)", "xi + 1", "Error Absoluto", "F(xi)", "F'(xi)"):
                if col == "#":
                    self.tablaTrv.heading("#", text="#")
                    self.tablaTrv.column("#", width=30, anchor='center')
                else:
                    self.tablaTrv.heading(col, text=col)
                    self.tablaTrv.column(col, width=150, anchor='w')
        elif tipo == "Método de la Secante":

            ttk.Label(self.valorIni, text="Valor Inicial #1 (xi - 1)", font=(None, 11, 'bold')).pack(anchor='center', pady=4)
            self.val_K = ttk.Entry(self.valorIni, width=13)
            self.val_K.pack(anchor='center', pady=5)

            ttk.Label(self.valorIni, text="Valor Inicial #2 (xi)", font=(None, 11, 'bold')).pack(anchor='center', pady=4)
            self.val_J = ttk.Entry(self.valorIni, width=13)
            self.val_J.pack(anchor='center', pady=5)

            ttk.Label(self.valorIni, text="Tolerancia", font=(None, 11, 'bold')).pack(anchor='center', pady=4)
            self.tol = ttk.Entry(self.valorIni, textvariable=self.tolerancia, width=13)
            self.tol.pack(anchor='center', pady=5)

            ctk.CTkButton(self.valorIni, text="Encontrar Respuesta", command=self.resolverEcuacion, fg_color='#3b8b87').pack(anchor='center', pady=10)
            
            # TABLA TREEVIEW
            self.tablaTrv = ttk.Treeview(self.procedimiento, columns=("#", "xi - 1", "xi", "xi + 1", "Error Absoluto", "F(xi - 1)", "F(xi)"), show='headings')
            self.tablaTrv.pack(fill='both', expand=True)

            for col in ("#", "xi - 1", "xi", "xi + 1", "Error Absoluto", "F(xi - 1)", "F(xi)"):
                if col == "#":
                    self.tablaTrv.heading("#", text="#")
                    self.tablaTrv.column("#", width=30, anchor='center')
                else:
                    self.tablaTrv.heading(col, text=col)
                    self.tablaTrv.column(col, width=150, anchor='w')

    def resolverEcuacion(self):
        metodo_num = self.tipo_metnum.get()
        
        funcion = self.ecuacion.get().strip()

        for num in self.superindices:

            funcion = funcion.replace(self.superindices[num], f"**{num}")

        funcion = funcion.replace("^", "**")
        funcion = funcion.replace("√", "sqrt")
        funcion = funcion.replace("log", "log10")
        funcion = funcion.replace("ln", "log")
        funcion = funcion.replace("e", str(numpy.e))
        funcion = funcion.replace(f"s{str(numpy.e)}c", "sec")
        funcion = funcion.replace("π", str(numpy.pi))
        funcion = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', funcion)
        # MÉTODOS CERRADOS

        if metodo_num == 'met_cerr':
            metodo_cerr = self.metodosCerrados.get()
            if metodo_cerr == 'Método de Bisección':
                try:
                    lim_inferior = float(self.limI.get().strip())
                    lim_superior = float(self.limS.get().strip())

                    # Si no se especifica la tolerancia, entonces el valor por defecto va a ser 0.00001
                    if self.tol.get().strip() == "":
                        err = 0.00001

                    else:
                        err = float(self.tol.get().strip())

                    self.tablaTrv.delete(*self.tablaTrv.get_children())

                    resultados, resp = metodoBiseccion(lim_inferior, lim_superior, funcion, err)
                    for fila in resultados:
                        self.tablaTrv.insert("", tk.END, values=fila)

                    for w in self.respuestaNum.winfo_children():
                        w.destroy()

                    ttk.Label(self.respuestaNum, text=f"Respuesta: {resp} (La respuesta se puede ver en la última iteración, si es que se realizaron)", font=('Cambria', 14, 'bold')).pack(anchor='center',pady=3)

                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error: {e}")

            elif metodo_cerr == 'Método de Falsa Posición':
                try:
                    lim_inferior = float(self.limI.get().strip())
                    lim_superior = float(self.limS.get().strip())

                    # Si no se especifica la tolerancia, entonces el valor por defecto va a ser 0.00001
                    if self.tol.get().strip() == "":
                        err = 0.00001

                    else:
                        err = float(self.tol.get().strip())

                    self.tablaTrv.delete(*self.tablaTrv.get_children())

                    resultados, resp = reglaFalsa(lim_inferior, lim_superior, funcion, err)
                    for fila in resultados:
                        self.tablaTrv.insert("", tk.END, values=fila)

                    for w in self.respuestaNum.winfo_children():
                        w.destroy()

                    ttk.Label(self.respuestaNum, text=f"Respuesta: {resp} (La respuesta se puede ver en la última iteración, si es que se realizaron)", font=('Cambria', 14, 'bold')).pack(anchor='center',pady=3)

                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error: {e}")

            else:
                messagebox.showerror(title="Método no definido", message="No se ha definido el método para encontrar la raíz de la ecuación")

        # MÉTODOS ABIERTOS

        elif metodo_num == 'met_abier':
            metodo_abier = self.metodosAbiertos.get()

            if metodo_abier == "Método de Newton-Raphson":
                try:
                    valorInicial = float(self.val_I.get().strip())

                    # Si no se especifica la tolerancia, entonces el valor por defecto va a ser 0.00001
                    if self.tol.get().strip() == "":
                        err = 0.00001

                    else:
                        err = float(self.tol.get().strip())

                    self.tablaTrv.delete(*self.tablaTrv.get_children())

                    resultados, resp = metodoNewton(valorInicial, funcion, err)

                    for fila in resultados:
                        self.tablaTrv.insert("", tk.END, values=fila)

                    for w in self.respuestaNum.winfo_children():
                        w.destroy()

                    ttk.Label(self.respuestaNum, text=f"Respuesta: {resp} (La respuesta se puede ver en la última iteración, si es que se realizaron)", font=('Cambria', 14, 'bold')).pack(anchor='center',pady=3)

                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error: {e}")
            elif metodo_abier == "Método de la Secante":

                try:
                    v1 = float(self.val_K.get().strip())
                    v2 = float(self.val_J.get().strip())

                    # Si no se especifica la tolerancia, entonces el valor por defecto va a ser 0.00001
                    if self.tol.get().strip() == "":
                        err = 0.00001

                    else:
                        err = float(self.tol.get().strip())

                    self.tablaTrv.delete(*self.tablaTrv.get_children())

                    resultados, resp = metodoSecante(v1, v2, funcion, err)

                    for fila in resultados:
                        self.tablaTrv.insert("", tk.END, values=fila)

                    for w in self.respuestaNum.winfo_children():
                        w.destroy()

                    ttk.Label(self.respuestaNum, text=f"Respuesta: {resp} (La respuesta se puede ver en la última iteración, si es que se realizaron)", font=('Cambria', 14, 'bold')).pack(anchor='center',pady=3)

                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error: {e}")
            else:
                messagebox.showerror(title="Método no definido", message="No se ha definido el método para encontrar la raíz de la ecuación")

    def graficarFuncion(self):

        ecua = self.ecuacion.get().strip()
        
        for e in self.grafica.winfo_children():
            e.destroy()

        for num in self.superindices:

            ecua = ecua.replace(self.superindices[num], f"**{num}")

        try:
            x = Symbol('x')
        
            ecua = ecua.replace("^", "**")
            ecua = ecua.replace("log", "log10")
            ecua = ecua.replace("ln", "log")
            ecua = ecua.replace("√", "sqrt")
            ecua = ecua.replace("e", str(numpy.e))
            ecua = ecua.replace(f"s{str(numpy.e)}c", "sec")
            ecua = ecua.replace("π", str(numpy.pi))

            ecua = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', ecua)

            nuevaEcua = sympify(ecua)

            func = lambdify(x, nuevaEcua, modules=["numpy"])

            ejeX = numpy.linspace(-10, 10, 400)

            with numpy.errstate(divide='ignore', invalid='ignore'):
                ejeY = func(ejeX)

            # Limpiar valores no numéricos
            ejeY = numpy.array(ejeY, dtype=float)
            ejeY[~numpy.isfinite(ejeY)] = numpy.nan

            # Crear figura
            fig = Figure(figsize=(4, 6), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(ejeX, ejeY, color="red")

            # Límites de la gráfica en X y Y
            ax.set_xlim(-10, 10)
            ax.set_ylim(-10, 10)

            # Separadores/números en la gráfica
            ax.set_xticks(numpy.arange(-10, 11, 2))
            ax.set_yticks(numpy.arange(-10, 11, 2))

            # --- CONFIGURAR COMO PLANO CARTESIANO ---
            ax.spines["top"].set_color("none")      # Quita borde superior
            ax.spines["right"].set_color("none")    # Quita borde derecho
            ax.spines["left"].set_position("zero")  # Eje Y pasa por x=0
            ax.spines["bottom"].set_position("zero")# Eje X pasa por y=0

            ax.set_aspect("auto")                   # Mantiene proporción libre
            ax.grid(True, linestyle="--", linewidth=0.6)
            ax.set_title(f"Gráfica de y = {self.ecuacion.get().strip()}", fontsize=12)

            # Mostrar en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.grafica)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        except:
            messagebox.showerror(title="Error a la hora de graficar", message="Algo salió mal a la hora de grafica la función")

    def _build_ui(self):
        # Selección de tipo de operación
        top = ctk.CTkFrame(self.ventanaPrincipal, fg_color='#0b5c71')
        top.pack(side='top', fill='x', pady=5)

        # Botones de acciones
        ctk.CTkButton(top, text="Generar entradas", font=('Georgia', 20, 'bold'), height=35, command=self.generar_entradas, fg_color='#e6e6e6', text_color="#000000").pack(side='left', padx=5)
        ctk.CTkButton(top, text="Resolver", font=('Georgia', 20, 'bold'), height=35, command=self.resolver, fg_color='#e6e6e6', text_color="#06a900").pack(side='left', padx=5)
        ctk.CTkButton(top, text="Limpiar", font=('Georgia', 20, 'bold'), height=35, command=self.limpiar, fg_color="#ff9292", text_color="#000000").pack(side='left', padx=5)
        ctk.CTkButton(top, text="Volver al menú", font=('Georgia', 20, 'bold'), height=35, command=lambda: [self.ventanaPrincipal.wm_withdraw(), self.menuPrincipal.wm_deiconify(), self.maximizarVentana(self.menuPrincipal)], fg_color='#e6e6e6', text_color="#ff0000").pack(side='right', padx=5)


        paned = ttk.Panedwindow(self.ventanaPrincipal, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Izquierda: Crear siete botones de manera vertical que reemplacen las acciones del raddiobutton
        izquierda = ttk.Frame(paned)
        paned.add(izquierda, weight=0)

        # Botones de opciones
        botones = [("Sistemas", "sistemas"),("Suma","suma"),("Multiplicación","multiplicacion"),("Transpuesta","transpuesta"),("Independencia Lineal","independencia"),("Inversa","inversa"),("Determinante","det")]

        for texto, metodo in botones:

            ctk.CTkButton(izquierda, text=texto, font=('Georgia', 22, 'bold'), width=200, height=60, fg_color='#3b8b87', command=lambda m=metodo: [self.metodo.set(m), self._on_method_change()]).pack(fill='x', pady=20, padx=(0,10))

        # Barras de desplazamiento para las entradas
        centro = ttk.Frame(paned, width=420)
        paned.add(centro, weight=0)

        self.canvas = tk.Canvas(centro)
        self.canvas.configure(background='#0b5c71')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vbar = ttk.Scrollbar(centro, orient=tk.VERTICAL, command=self.canvas.yview)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=vbar.set)
        self.entradas_contenedor = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.entradas_contenedor, anchor='nw')
        self.entradas_contenedor.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Derecha: El log y la pantalla de resultados
        derecha = ttk.Frame(paned)
        paned.add(derecha, weight=0)

        cuadro_registro = ctk.CTkFrame(derecha, fg_color='#0b5c71')
        cuadro_registro.pack(fill='both', expand=True)

        ctk.CTkLabel(cuadro_registro, text="Registro (paso a paso):", font=('Georgia',14,'bold'), fg_color='#0b5c71', text_color='#e6e6e6').pack(anchor='w', padx=5, pady=(5,0))

        # Log con fuente monoespaciada y fondo blanco para legibilidad
        self.log_texto = ctk.CTkTextbox(cuadro_registro, height=24, state='disabled', fg_color='#ffffff', text_color='black', font=('Consolas', 14), padx=5, pady=5)
        self.log_texto.pack(side='left', fill='both', expand=True)

        log_scroll = ctk.CTkScrollbar(cuadro_registro, orientation='vertical', command=self.log_texto.yview, fg_color='#ffffff', button_color='#3b8b87', button_hover_color='#0d6462')
        log_scroll.pack(side='right', fill='y')
        self.log_texto.configure(yscrollcommand=log_scroll.set)

        ctk.CTkLabel(derecha, text="Resultado / Soluciones:", font=('Georgia',14,'bold'), fg_color='#0b5c71', text_color='#e6e6e6').pack(anchor='w', padx=5, pady=(5,0))
        self.result_var = tk.StringVar(value='-')

        # Caja de resultado con fondo blanco y relieve para destacarla
        ctk.CTkLabel(derecha, textvariable=self.result_var, fg_color='white', text_color='black', corner_radius=8, height=40).pack(fill='x', padx=(5,0), pady=(0,5))

        # inicial
        self._on_method_change()

    def _on_method_change(self):
        metodo = self.metodo.get()

        # Limpiar la zona de entradas y generar instrucciones
        for w in self.entradas_contenedor.winfo_children():
            w.destroy()

        ttk.Label(self.entradas_contenedor, text="Instrucciones de Entrada:\n", font=('Helvetica',14,'bold')).pack(anchor='w')

        cuadro_marco = ttk.Frame(self.entradas_contenedor)
        cuadro_marco.pack(anchor='w')

        # Si la operación solo necesita una matriz
        def fils_col():
            ttk.Label(cuadro_marco, text="Filas (n):", font=('Helvetica',12,'bold')).grid(row=0, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
            ttk.Label(cuadro_marco, text="Columnas (m):", font=('Helvetica',12,'bold')).grid(row=1, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_var_var, width=6).grid(row=1, column=1, padx=4)

        # Si la operación utiliza dos matrices
        def a_b():
            # Cambio de mensaje si es suma
            if metodo == 'suma':
                ttk.Label(cuadro_marco, text="Filas:", font=('Helvetica',12,'bold')).grid(row=0, column=0, padx=7, pady=2)
                ttk.Label(cuadro_marco, text="Columnas:", font=('Helvetica',12,'bold')).grid(row=0, column=2, padx=7, pady=2)
            else:
                ttk.Label(cuadro_marco, text="Filas para A:", font=('Helvetica',12,'bold')).grid(row=0, column=0, padx=7, pady=2)
                ttk.Label(cuadro_marco, text="Columnas para A:", font=('Helvetica',12,'bold')).grid(row=0, column=2, padx=7, pady=2)
            
            ttk.Entry(cuadro_marco, textvariable=self.matA_filas, width=4).grid(row=0, column=1)
            ttk.Entry(cuadro_marco, textvariable=self.matA_columnas, width=4).grid(row=0, column=3)
            # Cambio de ubicación de escalar si es suma
            if metodo == 'suma':
                ttk.Label(cuadro_marco, text="Escalar para A:", font=('Helvetica',12,'bold')).grid(row=1, column=0, padx=7, pady=2)
                ttk.Entry(cuadro_marco, textvariable=self.matA_escalar, width=4).grid(row=1, column=1)
            else:
                ttk.Label(cuadro_marco, text="Escalar para A:", font=('Helvetica',12,'bold')).grid(row=2, column=0, padx=7, pady=2)
                ttk.Entry(cuadro_marco, textvariable=self.matA_escalar, width=4).grid(row=2, column=1)
            # Ingreso de valores para B si es multiplicación
            if metodo == 'multiplicacion':                
                ttk.Label(cuadro_marco, text="Filas para B:", font=('Helvetica',12,'bold')).grid(row=1, column=0, padx=7, pady=2)
                ttk.Entry(cuadro_marco, textvariable=self.matB_filas, width=4).grid(row=1, column=1)
                ttk.Label(cuadro_marco, text="Columnas para B:", font=('Helvetica',12,'bold')).grid(row=1, column=2, padx=7, pady=2)
                ttk.Entry(cuadro_marco, textvariable=self.matB_columnas, width=4).grid(row=1, column=3)
            # Cambio de ubicación de escalar si es suma
            if metodo == 'suma':
                ttk.Label(cuadro_marco, text="Escalar para B:", font=('Helvetica',12,'bold')).grid(row=1, column=2, padx=7, pady=2)
                ttk.Entry(cuadro_marco, textvariable=self.matB_escalar, width=4).grid(row=1, column=3)
            else:
                ttk.Label(cuadro_marco, text="Escalar para B:", font=('Helvetica',12,'bold')).grid(row=2, column=2, padx=7, pady=2)
                ttk.Entry(cuadro_marco, textvariable=self.matB_escalar, width=4).grid(row=2, column=3)

        # EN ESTA PARTE SE EXPLICA LOS PROCEDIMIENTOS A SEGUIR
        
        if metodo == 'sistemas':
            ttk.Label(cuadro_marco, text="1. Seleccione el método para resolver\nel sistema de ecuaciones.", font=('Helvetica',14,'normal')).grid(row=0,column=0,pady=3, sticky='w')

            ttk.Label(cuadro_marco, text="2. Ingrese el número de ecuaciones del\nsistema", font=('Helvetica',14,'normal')).grid(row=1,column=0,pady=3, sticky='w')
            ttk.Label(cuadro_marco, text="3. Genere los cuadros de entradas, y en \ncada uno, ingrese la ecuación", font=('Helvetica',14,'normal')).grid(row=2,column=0,pady=3, sticky='w')
            ttk.Label(cuadro_marco, text="4. Una vez ingresadas las ecuaciones, si\ndesea, haga clic en 'Forma Matricial'.\nSi no, haga clic en 'Resolver'", font=('Helvetica',14,'normal')).grid(row=3,column=0,pady=3, sticky='w')

            # Una pequeña nota al usuario, sobre cómo debe ingresar cada ecuación
            ttk.Label(cuadro_marco, text="Nota: Para las incógnitas, escribalas como\nx1, x2, x3 y asísucesivamente.", font=('Helvetica',14,'normal')).grid(row=4,column=0,pady=3, sticky='w')

            ttk.Label(cuadro_marco, text="N° de ecuaciones:", font=('Helvetica',12,'bold')).grid(row=5,column=0, pady=10, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=5,column=0,padx=5)
            self.opciones = ctk.CTkComboBox(cuadro_marco, variable=self.metodoEscoger, width=230, values=('Gauss-Jordan','Gauss','Regla de Cramer'), state='readonly', font=('Helvetica', 14, 'bold'))
            self.opciones.grid(row=6,column=0,pady=3, sticky='w')

        elif metodo in ('suma','multiplicacion'):
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas\nde las dos matrices.", font=('Helvetica',14,'normal')).pack(anchor='w')
            a_b()
            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de las matrices.\n3. Digite los valores de cada matriz.", font=('Helvetica',14,'normal')).pack(anchor='w')
            ttk.Label(self.entradas_contenedor, text="(Si no se especifica el escalar para alguna\nde las matrices, entonces el escalar\nserá 1)", font=('Helvetica',14,'normal')).pack(anchor='w')
            self.aplicar_At = ctk.CTkCheckBox(self.entradas_contenedor,text="Aplicar transpuesta para A", font=('Helvetica',16,'bold'), hover_color="#5E5E5E", checkmark_color="#00ff40")
            self.aplicar_At.pack(anchor='w', pady=10, padx=2)

            self.aplicar_Bt = ctk.CTkCheckBox(self.entradas_contenedor,text="Aplicar transpuesta para B", font=('Helvetica',16,'bold'), hover_color="#5E5E5E", checkmark_color="#00ff40")
            self.aplicar_Bt.pack(anchor='w', pady=4, padx=2)

        elif metodo in ('transpuesta', 'inversa', 'det'):
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas\nde la matriz inicial.", font=('Helvetica',14,'normal')).pack(anchor='w')
            fils_col()
            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de la matriz.\n3. Digite los valores de la matriz.", font=('Helvetica',14,'normal')).pack(anchor='w')

        elif metodo == 'independencia':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de vectores (columnas)\ny entradas (filas).", font=('Helvetica',14,'normal')).pack(anchor='w')
            
            # Se generan los cuadros para los vectores
            ttk.Label(cuadro_marco, text="Entradas por vector (n):", font=('Helvetica',14,'bold')).grid(row=0, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
            ttk.Label(cuadro_marco, text="N° de vectores (m):", font=('Helvetica',14,'bold')).grid(row=1, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_var_var, width=6).grid(row=1, column=1, padx=4)

            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de cada vector.\n3. Digite los valores de cada vector.", font=('Helvetica',14,'normal')).pack(anchor='w')

        else:
            ttk.Label(self.entradas_contenedor, text="Seleccione un método\nde operación.", font=('Helvetica',24,'bold')).pack(anchor='w')

    def generar_entradas(self):
        
        for w in self.entradas_contenedor.winfo_children():
            
            # Se actualiza la parte donde se ingresan las entradas
            w.destroy()
            self._on_method_change()
        
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

            ttk.Label(self.entradas_contenedor,text="Sistema lineal:", font=('Helvetica',12,'bold')).pack(anchor='w')
            
            grid_e = ttk.Frame(self.entradas_contenedor)
            grid_e.pack(anchor='w')

            # entradas
            for i in range(n):
                filas_entrada = []

                ttk.Label(grid_e, text=f"Ec {i + 1}:", font=('Helvetica',12,'bold'), padding=5).grid(row=i, column=0, pady=2)
                
                e_b = ttk.Entry(grid_e, width=30, font=('Helvetica',12,'normal'))
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

            ttk.Label(self.entradas_contenedor, text=f'Matriz A ({r}×{c})', font=('Helvetica',12,'bold')).pack(anchor='center')
            frameA = ttk.Frame(self.entradas_contenedor); frameA.pack(pady=4)
            for i in range(r):
                fila = []
                for j in range(c):
                    e = ttk.Entry(frameA, width=10)
                    e.grid(row=i, column=j, padx=2, pady=2)
                    fila.append(e)
                self.entradas_A.append(fila)

            ttk.Label(self.entradas_contenedor, text=f'Matriz B ({r}×{c})', font=('Helvetica',12,'bold')).pack(anchor='center')
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
                    messagebox.showerror('Incompatibilidad', 'La cantidad de columnas de A, debe ser igual a la cantidad de filas de B')
                    return
            except Exception:
                messagebox.showerror('Entrada inválida', 'Dimensiones deben ser enteros positivos y compatibles.')
                return

            ttk.Label(self.entradas_contenedor, text=f'Matriz A ({r}×{k})', font=('Helvetica',12,'bold')).pack(anchor='center')
            frameA = ttk.Frame(self.entradas_contenedor); frameA.pack(pady=4)
            for i in range(r):
                fila = []
                for j in range(k):
                    e = ttk.Entry(frameA, width=10)
                    e.grid(row=i, column=j, padx=2, pady=2)
                    fila.append(e)
                self.entradas_A.append(fila)

            ttk.Label(self.entradas_contenedor, text=f'Matriz B ({k}×{c})', font=('Helvetica',12,'bold')).pack(anchor='center')
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

            ttk.Label(self.entradas_contenedor, text=f'Matriz: {n} filas × {m} columnas', font=('Helvetica',12,'bold')).pack(anchor='center')
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
                ttk.Label(grid, text=f'v{j+1}', anchor='center', width=10, font=('Helvetica',12,'bold')).grid(row=0, column=j)
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

                    # Se verifica si las opciones 'Aplicar transpuesta para...' fueran marcadas o no
                    if self.aplicar_At._check_state == True:

                        print("Para la transpuesta de la matriz A", end="")
                        A = transpuestamatriz(A)
                    
                    if self.aplicar_Bt._check_state == True:

                        print("Para la transpuesta de la matriz B", end="")
                        B = transpuestamatriz(B)
                    
                    print("\nSUMA DE MATRICES")
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

                    # Se verifica si las opciones 'Aplicar transpuesta para...' fueran marcadas o no
                    if self.aplicar_At._check_state == True:

                        print("Para la transpuesta de la matriz A", end="")
                        A = transpuestamatriz(A)
                    
                    if self.aplicar_Bt._check_state == True:

                        print("Para la transpuesta de la matriz B", end="")
                        B = transpuestamatriz(B)

                    print("\nMULTIPLICACIÓN DE MATRICES")
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

    def _close_from_subwindow(self, ventana):
        """Maneja el cierre cuando se cierra una subventana.

        Destruye la ventana principal (`menuPrincipal`) para asegurarse de
        que la aplicación termine por completo cuando el usuario cierre
        una subventana usando el botón de cierre de la ventana.
        """
        try:
            if hasattr(self, 'menuPrincipal') and self.menuPrincipal:
                try:
                    self.menuPrincipal.destroy()
                except Exception:
                    # Si falla destruir, intentar forzar la destrucción de la subventana
                    try:
                        ventana.destroy()
                    except Exception:
                        pass
            else:
                try:
                    ventana.destroy()
                except Exception:
                    pass
        except Exception:
            try:
                ventana.destroy()
            except Exception:
                pass
