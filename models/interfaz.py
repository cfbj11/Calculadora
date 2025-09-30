# models/interfaz.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from contextlib import redirect_stdout
import io

from models.eliminacion import eliminacionGaussJordan, eliminacionGauss
from models.operaciones import suma_matrices, multiplicar_matrices

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
        self.ventanaPrincipal.title("Calculadora de Matrices — Gauss-Jordan / Suma / Multiplicación")
        self.ventanaPrincipal.geometry("1100x720")

        # Variables
        self.metodo = tk.StringVar(value="gaussjordan")
        self.num_eq_var = tk.StringVar(value="")
        self.num_var_var = tk.StringVar(value="")
        self.matA_filas = tk.StringVar(value="")
        self.matA_columnas = tk.StringVar(value="")
        self.matB_filas = tk.StringVar(value="")
        self.matB_columnas = tk.StringVar(value="")

        # Grids de entrada
        self.entradas_aug = []
        self.entradas_A = []
        self.entradas_B = []

        self._build_ui()

    def _build_ui(self):
        # Selección de tipo de operación
        top = ttk.Frame(self.ventanaPrincipal, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Operación:", font=(None, 11, "bold")).pack(side=tk.LEFT)
        for val, label in [("gaussjordan", "Gauss-Jordan"), ("gauss", "Gauss"),
                        ("suma", "Suma"), ("multiplicacion", "Multiplicación")]:
            ttk.Radiobutton(top, text=label, variable=self.metodo, value=val, command=self._on_method_change).pack(side=tk.LEFT, padx=6)

        params = ttk.Frame(top)
        params.pack(side=tk.LEFT, padx=12)
        ttk.Label(params, text="Filas (n):").grid(row=0, column=0, sticky='w')
        ttk.Entry(params, textvariable=self.num_eq_var, width=6).grid(row=0, column=1, padx=4)
        ttk.Label(params, text="Columnas (m):").grid(row=0, column=2, sticky='w', padx=(8,0))
        ttk.Entry(params, textvariable=self.num_var_var, width=6).grid(row=0, column=3, padx=4)

        mat_frame = ttk.Frame(top)
        mat_frame.pack(side=tk.LEFT)
        ttk.Label(mat_frame, text="*A: filas").grid(row=0, column=0)
        ttk.Entry(mat_frame, textvariable=self.matA_filas, width=4).grid(row=0, column=1)
        ttk.Label(mat_frame, text="cols").grid(row=0, column=2)
        ttk.Entry(mat_frame, textvariable=self.matA_columnas, width=4).grid(row=0, column=3)

        ttk.Label(mat_frame, text="B: filas").grid(row=1, column=0)
        ttk.Entry(mat_frame, textvariable=self.matB_filas, width=4).grid(row=1, column=1)
        ttk.Label(mat_frame, text="cols").grid(row=1, column=2)
        ttk.Entry(mat_frame, textvariable=self.matB_columnas, width=4).grid(row=1, column=3)

        # Botones
        botones = ttk.Frame(self.ventanaPrincipal, padding=6)
        botones.pack(fill=tk.X)
        ttk.Button(botones, text="Generar entradas", command=self.generar_entradas).pack(side=tk.LEFT, padx=6)
        ttk.Button(botones, text="Resolver / Ejecutar", command=self.resolver).pack(side=tk.LEFT, padx=6)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side=tk.LEFT, padx=6)
        ttk.Button(botones, text="Guardar registro", command=self._guardar_log).pack(side=tk.RIGHT, padx=6)

        paned = ttk.Panedwindow(self.ventanaPrincipal, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        izquierda = ttk.Frame(paned)
        paned.add(izquierda, weight=1)

        # Barras de desplazamiento para las entradas
        self.canvas = tk.Canvas(izquierda)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vbar = ttk.Scrollbar(izquierda, orient=tk.VERTICAL, command=self.canvas.yview)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=vbar.set)
        self.entradas_contenedor = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.entradas_contenedor, anchor='nw')
        self.entradas_contenedor.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Derecha: El log y la pantalla de resultados
        derecha = ttk.Frame(paned, width=420)
        paned.add(derecha, weight=0)
        ttk.Label(derecha, text="Registro (paso a paso):", font=(None,10,'bold')).pack(anchor='w')
        self.log_texto = tk.Text(derecha, height=24, state='disabled')
        self.log_texto.pack(fill=tk.BOTH, expand=True)
        log_scroll = ttk.Scrollbar(derecha, orient=tk.VERTICAL, command=self.log_texto.yview)
        log_scroll.place(relx=1.0, rely=0, relheight=1.0, anchor='ne')
        self.log_texto.configure(yscrollcommand=log_scroll.set)

        ttk.Label(derecha, text="Resultado / Soluciones:", font=(None,10,'bold')).pack(anchor='w', pady=(6,0))
        self.result_var = tk.StringVar(value='-')
        result_box = ttk.Label(derecha, textvariable=self.result_var, background='white', relief='sunken', padding=6)
        result_box.pack(fill=tk.X)

        # inicial
        self._on_method_change()

    def _on_method_change(self):
        metodo = self.metodo.get()
        # Limpiar la zona de entradas y generar instrucciones
        for w in self.entradas_contenedor.winfo_children():
            w.destroy()
        if metodo in ('gauss', 'gaussjordan'):
            ttk.Label(self.entradas_contenedor, text="Matriz [(n) filas × (m) columnas]").pack(anchor='w')
        elif metodo == 'suma':
            ttk.Label(self.entradas_contenedor, text="Suma de matrices: generará dos matrices A y B con mismas dimensiones").pack(anchor='w')
        else:
            ttk.Label(self.entradas_contenedor, text="Multiplicación de matrices: generará A (r×k) y B (k×c)").pack(anchor='w')

    def generar_entradas(self):
        metodo = self.metodo.get()
        # limpiar
        for w in self.entradas_contenedor.winfo_children():
            w.destroy()

        self.entradas_aug = []
        self.entradas_A = []
        self.entradas_B = []

        if metodo in ('gauss', 'gaussjordan'):
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
                    e = ttk.Entry(grid, width=12)
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

    def _leer_matriz(self, entradas):
        M = []

        for i, r in enumerate(entradas):
            fila = []
            for j, e in enumerate(r):
                val = e.get().strip()
                if val == '':
                    val = '0'
                try:
                    num = float(val)
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
                if metodo == 'gaussjordan':
                    
                    if not self.entradas_aug:
                        raise ValueError('Primero genere la matriz aumentada (botón "Generar entradas").')
                    
                    matriz = self._leer_matriz(self.entradas_aug)

                    eliminacionGaussJordan(matriz, log_func=print)

                elif metodo == 'gauss':

                    if not self.entradas_aug:
                        raise ValueError('Primero genere la matriz aumentada (botón "Generar entradas").')
                    
                    matriz = self._leer_matriz(self.entradas_aug)
                    eliminacionGauss(matriz, log_func=print)
                elif metodo == 'suma':
                    if not self.entradas_A or not self.entradas_B:
                        raise ValueError('Genere las entradas de A y B primero.')
                    A = self._leer_matriz(self.entradas_A)
                    B = self._leer_matriz(self.entradas_B)
                    resultado = suma_matrices(A, B, log_func=print)
                    self.result_var.set("Suma realizada — ver registro")

                elif metodo == 'multiplicacion':
                    if not self.entradas_A or not self.entradas_B:
                        raise ValueError('Genere las entradas de A y B primero.')
                    A = self._leer_matriz(self.entradas_A)
                    B = self._leer_matriz(self.entradas_B)
                    resultado = multiplicar_matrices(A, B, log_func=print)
                    self.result_var.set("Multiplicación realizada — ver registro")

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
