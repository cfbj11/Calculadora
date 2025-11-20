from tkinter import messagebox
from sympy import sympify, symbols, lambdify, diff
import re
import numpy

def metodoNewton(valorInicial, funcion, error_conv):
    x = symbols('x')
    xa = valorInicial
    
    # Reemplazar operadores y corregir formato
    funcion = funcion.replace("^", "**")
    funcion = funcion.replace("√", "sqrt")
    funcion = funcion.replace("log", "log10")
    funcion = funcion.replace("ln", "log")
    funcion = funcion.replace("e", str(numpy.e))
    funcion = funcion.replace(f"s{str(numpy.e)}c", "sec")
    funcion = funcion.replace("π", str(numpy.pi))
    funcion = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', funcion)

    # Funciones
    func = sympify(funcion)
    derivada = diff(func, x)
    funcionArreglada = lambdify(x, func, modules=["numpy"])
    derivadaArreglada = lambdify(x, derivada, modules=["numpy"])

    try:

        # Evaluar valor inicial
        f_xa = funcionArreglada(xa)
        
        if f_xa == 0:

            messagebox.showinfo("Resultado", f"La raíz aproximada es {xa}, porque al evaluar el valor inicial en la función (o sea, {xa}), da 0")
            return [], xa
        else:
        
            resultados = []
            k = 1
            max_iter = 100
            xj_anterior = None

            while k <= max_iter:
            
                f_xa = funcionArreglada(xa)
                df_xa = derivadaArreglada(xa)
            
                xj = xa - (f_xa/df_xa)

                if numpy.isnan(xj):

                    messagebox.showerror(title="Error matemático", message="Durante los cálculos, se encontró con un valor no determinado (nan). Intente con otro valor")
                    return resultados, xa

                if xj_anterior is None:
                    Ea = 0
                else:
                    Ea = abs(xj - xj_anterior)

                # Agregar fila de resultados
                resultados.append((k, float(xa), float(xj), float(Ea), float(f_xa), float(df_xa)))

                if abs(Ea) < error_conv and k != 1:
                
                    messagebox.showinfo("Resultado", f"La raíz aproximada es {xj:.10f} \nNúmero de Iteraciones: {k}\nTolerancia: {error_conv}")
                    return resultados, xj

                xa = xj

                xj_anterior = xj
                k += 1

            messagebox.showwarning("Posible resultado", f"La raíz aproximada es {xj:.10f} \nNúmero de Iteraciones: {k}\nTolerancia: {error_conv}\nDebido a que se utilizaron la cantidad máxima de iteraciones permitidas, es probable que el resultado divergió. Intente con otro valor, y si vuelve a suceder lo mismo, eso es porque la función no tiene raíz")
            return resultados, xj
    except Exception:

        messagebox.showerror(title="Error matemático", message="Durante los cálculos, se encontró con un valor no determinado (nan). Intente con otro valor, y si vuelve a suceder lo mismo, eso es porque la función no tiene raíz")