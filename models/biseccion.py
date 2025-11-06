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

    if (a >= 0 and b >= 0): # lanza excepción si los dos salen positivos

        messagebox.showwarning(title="Signos iguales", message=f"No hay raíz en los intervalos, porque, al evaluar f(a) y f(b), tienen los signos iguales.\nf(a) ={a} y f(b) = {b}")
    elif a < 0 and b < 0: # lanza excepción si los dos salen negativos

        messagebox.showwarning(title="Signos iguales", message=f"No hay raíz en los intervalos, porque, al evaluar f(a) y f(b), tienen los signos iguales.\nf(a) ={a} y f(b) = {b}")
    elif i > s:
        
        messagebox.showerror(title="Inconsistencia", message="El límite inferior, es mayor que el superior")
    else:
        
        k = 1
        
        while True: # Bucle infinito

            print("Iteración:", k)
            
            print("Límite inferior:", i)
            print("Límite superior:", s)
            
            c = (i + s) / 2
            print("Punto medio:", c)
            
            m = funcionArreglada.subs(x, c).evalf() # Esto sería equivalente a f(c)
            print(f"Error en la iteración {k + 1}: {m}")

            if m < 0.00001 and m > -0.00001: # Si f(c) está entre -0.00001 y 0.00001

                messagebox.showinfo(title="Respuesta", message=f"La raíz de la función es {c}, y converge a {k} iteraciones")
                break

            if (a < 0 and m < 0) or (a >= 0 and m >= 0):

                i = c
            elif (b < 0 and m < 0) or (b >= 0 and m >= 0):

                s = c

            k += 1

            print("\n---------------------------------\n")