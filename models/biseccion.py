from tkinter import messagebox
from sympy import sympify, symbols
import re

def metodoBiseccion(limInf, limSup, funcion):

    x = symbols('x')
    i = limInf
    s = limSup
    
    funcion = funcion.replace("^", "**")

    funcion = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', funcion)

    # La vuelve simbólica la función
    funcionArreglada = sympify(funcion)

    a = funcionArreglada.subs(x, limInf).evalf()
    b = funcionArreglada.subs(x, limSup).evalf()
    print(a)
    print(b)

    if (a >= 0 and b >= 0): # lanza excepción si los dos salen positivos

        messagebox.showwarning(title="Signos iguales", message="No hay raíz en los intervalos, porque, al evaluar cada extremo del intervalo, tienen los signos iguales")
    elif a < 0 and b < 0: # lanza excepción si los dos salen negativos

        messagebox.showwarning(title="Signos iguales", message="No hay raíz en los intervalos, porque, al evaluar cada extremo del intervalo, tienen los signos iguales")
    else:
        
        k = 0
        
        while True: # Bucle infinito

            print("Límite inferior:", i)
            print("Límite superior:", s)
            
            c = (i + s) / 2
            print("Punto medio", c)
            
            m = funcionArreglada.subs(x, c).evalf()

            if m < 0.00001 and m > -0.00001:

                messagebox.showinfo(title="Respuesta", message=f"La raíz de la función es {c}, y converge a {k} iteraciones")
                break

            print(f"{i + 1}: {m}")
            if (a < 0 and m < 0) or (a >= 0 and m >= 0):

                i = c
            elif (b < 0 and m < 0) or (b >= 0 and m >= 0):

                s = c

            k += 1