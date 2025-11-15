from tkinter import messagebox
from sympy import sympify, symbols, lambdify
import re
import numpy

def reglaFalsa(limInf, limSup, funcion, error_conv):
    x = symbols('x')
    i = limInf
    s = limSup
    
    # Reemplazar operadores y corregir formato
    funcion = funcion.replace("^", "**")
    funcion = funcion.replace("√", "sqrt")
    funcion = funcion.replace("log", "log10")
    funcion = funcion.replace("ln", "log")
    funcion = funcion.replace("e", str(numpy.e))
    funcion = funcion.replace(f"s{str(numpy.e)}c", "sec")
    funcion = funcion.replace("π", str(numpy.pi))
    funcion = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', funcion)

    # La vuelve simbólica la función
    func = sympify(funcion)
    funcionArreglada = lambdify(x, func, modules=["numpy"])

    # Evaluar extremos
    f_a = funcionArreglada(i)
    f_b = funcionArreglada(s)

    if f_a == 0:

        messagebox.showinfo("Resultado", f"La raíz aproximada es {i}, porque al evaluar el límite inferior en la función (o sea, {i}), da 0")
        return [], f_a
    elif f_b == 0:

        messagebox.showinfo("Resultado", f"La raíz aproximada es {s}, porque al evaluar el límite superior (o sea, {s}) en la función, da 0")
        return [], f_b
    else:

        if i > s:
            messagebox.showerror(title="Inconsistencia", message="El límite inferior es mayor que el superior")
            return [], ""
        elif (f_a >= 0 and f_b >= 0) or (f_a < 0 and f_b < 0):
            messagebox.showwarning(
                title="Signos iguales",
                message=f"No hay raíz en los intervalos, porque f(a) y f(b) tienen los signos iguales.\nf(a) ={f_a} y f(b) = {f_b}")
            return [], ""
        
        resultados = []
        k = 1
        max_iter = 100
        c_anterior = None

        while k <= max_iter:

            f_a = funcionArreglada(i)
            f_b = funcionArreglada(s)
            
            c = ((s * f_a) - (i * f_b))/(f_a - f_b)
            f_c = funcionArreglada(c)

            if c_anterior is None:
                Ea = 0
            else:
                Ea = abs(c - c_anterior)

            # Agregar fila de resultados
            resultados.append((k, float(i), float(s), float(c), float(Ea), float(f_a), float(f_b), float(f_c)))

            if abs(f_c) < error_conv:
                
                messagebox.showinfo("Resultado", f"La raíz aproximada es {c:.10f} \nNúmero de Iteraciones: {k}\nError: {error_conv}")
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

        return resultados, c