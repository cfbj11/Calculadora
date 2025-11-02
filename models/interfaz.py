# models/interfaz.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from contextlib import redirect_stdout

from fractions import Fraction

from models.eliminacion import eliminacionGaussJordan, eliminacionGauss
from models.operaciones import suma_matrices, multiplicar_matrices
from models.transpuesta import transpuestamatriz
from models.independencia import independenciaLineal
from models.inversa import inversaMatriz
from models.determinante import detMatriz
from models.cramer import reglaCramer

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
    def __init__(self):
        self.ventanaPrincipal = tk.Tk()
        self.ventanaPrincipal.title("Calculadora de Matrices")
        self.ventanaPrincipal.geometry("1350x720")
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

        # Configuración de estilos (tema y apariencia)
        # Usamos ttk.Style para aplicar una apariencia más moderna y coherente
        self.style = ttk.Style(self.ventanaPrincipal)
        try:
            # 'clam' suele permitir más personalización en Windows y Linux
            self.style.theme_use('clam')
        except Exception:
            pass
        # Tipografías y colores base
        default_font = ('Segoe UI', 10)
        heading_font = ('Segoe UI', 11, 'bold')
        # Configuraciones generales
        self.style.configure('TLabel', font=default_font, background='#0b5c71', foreground='#e6e6e6')
        self.style.configure('TFrame', background='#0b5c71')
        self.style.configure('TButton', font=default_font, padding=6)
        self.style.configure('TEntry', font=default_font)
        self.style.configure('TCombobox', font=default_font)
        # Botón destacado
        self.style.configure('Accent.TButton', font=default_font, padding=8, foreground='white', background='#3b8b87')
        self.style.map('Accent.TButton', background=[('active', '#e6e6e6'), ('!disabled', '#3b8b87')])
        # Resultado
        self.style.configure('Result.TLabel', background='white', padding=6, font=default_font)
        # Fondo de la ventana
        try:
            self.ventanaPrincipal.configure(background='#0b5c71')
        except Exception:
            pass

        # Variables
        self.metodo = tk.StringVar(value="sistemas")
        self.num_eq_var = tk.StringVar(value="")
        self.num_var_var = tk.StringVar(value="")
        self.matA_filas = tk.StringVar(value="")
        self.matA_columnas = tk.StringVar(value="")
        self.matA_escalar = tk.StringVar(value="")
        self.matB_filas = tk.StringVar(value="")
        self.matB_columnas = tk.StringVar(value="")
        self.matB_escalar = tk.StringVar(value="")

        # Grids de entrada
        self.entradas_aug = []
        self.entradas_A = []
        self.entradas_B = []

        self._build_ui()

    def _build_ui(self):
        # Selección de tipo de operación
        top = ttk.Frame(self.ventanaPrincipal, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        # Botones
        ttk.Button(top, text="Generar entradas", command=self.generar_entradas, style='Accent.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Resolver / Ejecutar", command=self.resolver, style='Accent.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Limpiar", command=self.limpiar, style='Accent.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Guardar registro", command=self._guardar_log, style='Accent.TButton').pack(side=tk.RIGHT, padx=6)


        paned = ttk.Panedwindow(self.ventanaPrincipal, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Izquierda: Crear siete botones de manera vertical que reemplacen las acciones del raddiobutton
        izquierda = ttk.Frame(paned, width=420)
        paned.add(izquierda, weight=0)
        ttk.Button(izquierda, text="Sistemas", width=25, style='Accent.TButton', command=lambda: [self.metodo.set('sistemas'), self._on_method_change()]).pack(fill=tk.X, padx=2, pady=30)
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

        ttk.Label(self.entradas_contenedor, text="Instrucciones de Entrada:\n", font=(None,10,'bold')).pack(anchor='w', pady=(0,6))

        cuadro_marco = ttk.Frame(self.entradas_contenedor)
        cuadro_marco.pack(anchor='w')

        if metodo == 'sistemas':
            ttk.Label(self.entradas_contenedor, text="1. Seleccione el método para resolver el sistema de ecuaciones.").pack(anchor='w')
            self.opciones = ttk.Combobox(self.entradas_contenedor, values=('Gauss-Jordan','Gauss','Regla de Cramer'))
            self.opciones.pack(anchor='w')
            self.opciones.state(["readonly"])

            ttk.Label(self.entradas_contenedor, text="2. Ingrese el número de filas y columnas del sistema de ecuaciones.").pack(anchor='w')
            ttk.Label(cuadro_marco, text="Filas (n):").grid(row=0, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
            ttk.Label(cuadro_marco, text="Columnas (m):").grid(row=1, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_var_var, width=6).grid(row=1, column=1, padx=4)

            ttk.Label(self.entradas_contenedor, text="3. Genere las entradas.\n4. Digite los valores de cada ecuación.").pack(anchor='w')

        elif metodo == 'suma':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas en 'A'.").pack(anchor='w')
            ttk.Label(cuadro_marco, text="A => Filas:").grid(row=0, column=0)
            ttk.Entry(cuadro_marco, textvariable=self.matA_filas, width=4).grid(row=0, column=1)
            ttk.Label(cuadro_marco, text=", Columnas:").grid(row=0, column=2)
            ttk.Entry(cuadro_marco, textvariable=self.matA_columnas, width=4).grid(row=0, column=3)
            ttk.Label(cuadro_marco, text="Escalar para A: ").grid(row=1, column=0)
            ttk.Entry(cuadro_marco, textvariable=self.matA_escalar, width=4).grid(row=1, column=1)
            ttk.Label(cuadro_marco, text=", Escalar para B: ").grid(row=1, column=2)
            ttk.Entry(cuadro_marco, textvariable=self.matB_escalar, width=4).grid(row=1, column=3)

            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de las matrices.\n3. Digite los valores de cada matriz.").pack(anchor='w')
            ttk.Label(self.entradas_contenedor, text="(Si no se especifica la escalar para alguna de las matrices,\n entonces la escalar para dicha matriz será 1)").pack(anchor='w')

        elif metodo == 'multiplicacion':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas para las matrices A y B.").pack(anchor='w')
            ttk.Label(cuadro_marco, text="A => Filas:").grid(row=0, column=0)
            ttk.Entry(cuadro_marco, textvariable=self.matA_filas, width=4).grid(row=0, column=1)
            ttk.Label(cuadro_marco, text=", Columnas:").grid(row=0, column=2)
            ttk.Entry(cuadro_marco, textvariable=self.matA_columnas, width=4).grid(row=0, column=3)
            ttk.Label(cuadro_marco, text=", Escalar para A: ").grid(row=0, column=4)
            ttk.Entry(cuadro_marco, textvariable=self.matA_escalar, width=4).grid(row=0, column=5)
            ttk.Label(cuadro_marco, text="B => Filas: ").grid(row=1, column=0)
            ttk.Entry(cuadro_marco, textvariable=self.matB_filas, width=4).grid(row=1, column=1)
            ttk.Label(cuadro_marco, text=", Columnas: ").grid(row=1, column=2)
            ttk.Entry(cuadro_marco, textvariable=self.matB_columnas, width=4).grid(row=1, column=3)
            ttk.Label(cuadro_marco, text=", Escalar para B: ").grid(row=1, column=4)
            ttk.Entry(cuadro_marco, textvariable=self.matB_escalar, width=4).grid(row=1, column=5)

            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas para ambas matrices\n3. Digite los valores para cada matriz").pack(anchor='w')

        elif metodo == 'transpuesta':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas de la matriz inicial.").pack(anchor='w')
            ttk.Label(cuadro_marco, text="Filas (n):").grid(row=0, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
            ttk.Label(cuadro_marco, text="Columnas (m):").grid(row=1, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_var_var, width=6).grid(row=1, column=1, padx=4)

            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de la matriz.\n3. Digite los valores de la matriz.").pack(anchor='w')

        elif metodo == 'independencia':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de vectores(columnas) y entradas(filas).").pack(anchor='w')
            ttk.Label(cuadro_marco, text="Filas (n):").grid(row=0, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
            ttk.Label(cuadro_marco, text="Columnas (m):").grid(row=1, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_var_var, width=6).grid(row=1, column=1, padx=4)

            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de cada vector.\n3. Digite los valores de cada vector.").pack(anchor='w')

        elif metodo == 'inversa':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas de la matriz inicial.").pack(anchor='w')
            ttk.Label(cuadro_marco, text="Filas (n):").grid(row=0, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
            ttk.Label(cuadro_marco, text="Columnas (m):").grid(row=1, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_var_var, width=6).grid(row=1, column=1, padx=4)

            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de la matriz.\n3. Digite los valores de la matriz.").pack(anchor='w')

        elif metodo == 'det':
            ttk.Label(self.entradas_contenedor, text="1. Ingrese el número de filas y columnas de la matriz inicial.").pack(anchor='w')
            ttk.Label(cuadro_marco, text="Filas (n):").grid(row=0, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
            ttk.Label(cuadro_marco, text="Columnas (m):").grid(row=1, column=0, sticky='w')
            ttk.Entry(cuadro_marco, textvariable=self.num_var_var, width=6).grid(row=1, column=1, padx=4)

            ttk.Label(self.entradas_contenedor, text="2. Genere las entradas de la matriz.\n3. Digite los valores de la matriz.").pack(anchor='w')

    def generar_entradas(self):
        metodo = self.metodo.get()

        self.entradas_aug = []
        self.entradas_A = []
        self.entradas_B = []

        if metodo == 'sistemas':
            # generar matriz aumentada
            try:
                n = int(self.num_eq_var.get())
                m = int(self.num_var_var.get())
                if n <= 0 or m <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror('Entrada inválida', 'Ecuaciones e incógnitas deben ser enteros positivos.')
                return

            ttk.Label(self.entradas_contenedor, text=f'Matriz aumentada: {n} filas × {m} columnas').pack(anchor='w')

            grid = ttk.Frame(self.entradas_contenedor)
            grid.pack(pady=6)
            # encabezados
            for j in range(m - 1):
                ttk.Label(grid, text=f'x{j+1}', anchor='center', width=10).grid(row=0, column=j)
            ttk.Label(grid, text='b', width=10).grid(row=0, column=m - 1)
            # entradas
            for i in range(n):
                filas_entrada = []
                for j in range(m):
                    e = ttk.Entry(grid, width=6)
                    e.grid(row=i+1, column=j, padx=2, pady=2)
                    filas_entrada.append(e)
                self.entradas_aug.append(filas_entrada)

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
                    
                    matriz = self._leer_matriz(self.entradas_aug)

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
        
        self.ventanaPrincipal.mainloop()