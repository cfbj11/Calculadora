from tkinter import messagebox
from sympy import sympify, symbols, lambdify
import re
import numpy

def metodoSecante(valor1, valor2, funcion, error_conv):

    x = symbols('x')
    xi = valor1
    xj = valor2

    # Funciones
    func = sympify(funcion)
    funcionArreglada = lambdify(x, func, modules=["numpy"])

    f_xi = funcionArreglada(xi)
    f_xj = funcionArreglada(xj)

    try:

        if f_xi == 0:

            messagebox.showinfo("Resultado", f"La raíz aproximada es {xi}, porque al evaluar el valor inicial #1 en la función (o sea, {xi}), da 0")
            return [], xi
        elif f_xj == 0:

            messagebox.showinfo("Resultado", f"La raíz aproximada es {xj}, porque al evaluar el valor inicial #2 en la función (o sea, {xj}), da 0")
            return [], xj
        else:

            resultados = []
            k = 1
            max_iter = 100
            xs_anterior = None

            while k <= max_iter:

                f_xi = funcionArreglada(xi)
                f_xj = funcionArreglada(xj)

                xs = xj - ((f_xj)*(xi - xj))/(f_xi - f_xj)

                if numpy.isnan(xs):

                    messagebox.showerror(title="Error matemático", message="Durante los cálculos, se encontró con un valor no determinado (nan). Intente con otro valor")
                    return resultados, xs

                if xs_anterior is None:
                    Ea = 0
                else:
                    Ea = abs(xs - xs_anterior)

                # Agregar fila de resultados
                resultados.append((k, float(xi), float(xj), float(xs), float(Ea), float(f_xi), float(f_xj)))

                if abs(Ea) < error_conv and k != 1:
                
                    messagebox.showinfo("Resultado", f"La raíz aproximada es {xj:.10f} \nNúmero de Iteraciones: {k}\nTolerancia: {error_conv}")
                    return resultados, xj
                
                xi = xj
                xj = xs
                xs_anterior = xs
                k += 1
    except Exception:

        messagebox.showinfo("Error", "El algoritmo se detuvo, porque se encontró con un error matemático")