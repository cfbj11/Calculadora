from tkinter import messagebox
from sympy import sympify, symbols
import re
import numpy

def metodoBiseccion(limInf, limSup, funcion, error_conv = 0.0001):
    x = symbols('x')
    i = limInf
    s = limSup
    
    # Reemplazar operadores y corregir formato
    funcion = funcion.replace("^", "**")
    funcion = funcion.replace("e", str(numpy.e))
    funcion = funcion.replace("π", str(numpy.pi))
    funcion = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', funcion)

    # La vuelve simbólica la función
    funcionArreglada = sympify(funcion)

    # Evaluar extremos
    f_a = funcionArreglada.subs(x, i).evalf()
    f_b = funcionArreglada.subs(x, s).evalf()

    if f_a == 0:

        messagebox.showinfo("Resultado", f"La raíz aproximada es {i}, porque al evaluar el límite inferior en la función (o sea, {i}), da 0")
        return []
    elif f_b == 0:

        messagebox.showinfo("Resultado", f"La raíz aproximada es {s}, porque al evaluar el límite superior (o sea, {s}) en la función, da 0")
        return []
    else:
    
        if (f_a >= 0 and f_b >= 0) or (f_a <= 0 and f_b <= 0):
            messagebox.showwarning(
                title="Signos iguales",
                message=f"No hay raíz en los intervalos, porque f(a) y f(b) tienen los signos iguales.\nf(a) ={f_a} y f(b) = {f_b}")
            return []

        elif i > s:
            messagebox.showerror(title="Inconsistencia", message="El límite inferior es mayor que el superior")
            return []

        resultados = []
        k = 1
        max_iter = 100
        c_anterior = None
        
        while k <= max_iter:
            c = (i + s) / 2
            f_c = funcionArreglada.subs(x, c).evalf()

            # Calcular error porcentual
            if c_anterior is None:
                    Ea = 0
            else:
                if c == 0:
                    Ea = abs(c - c_anterior)
                else:
                    Ea = abs((c - c_anterior) / c) * 100

            # Agregar fila de resultados
            resultados.append((k, float(i), float(s), float(c), float(Ea), float(f_a), float(f_b), float(f_c)))

            # Condición de convergencia
            if Ea != 0:
                if Ea < error_conv * 100 or abs(f_c) < 1e-12:
                    messagebox.showinfo("Resultado", f"La raíz aproximada es {c:.10f} \nIteraciones. {k}")
                    break

            # Actualización de intervalos
            if f_a * f_c < 0:
                s = c
                f_b = f_c
            else:
                i = c
                f_a = f_c

            c_anterior = c
            k += 1

        return resultados