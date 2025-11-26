from models.imprimir_matriz import imprimir_matriz

def detMatriz(matriz):

    filas = len(matriz)
    columnas = len(matriz[0])

    columnaCero = False

    if filas != columnas:

        print("La matriz:")
        imprimir_matriz(matriz)
        print("\nNo es posible sacarle la determinante, debido a que la matriz no es cuadrada")
    else:

        det = 1 # Se inicializa con el valor de '1', para multiplicar por '-1', en caso de que hay intercambio de fila

        print("Matriz inicial:\n")
        imprimir_matriz(matriz, log_func=print)

        # Eliminación de filas hacia abajo
        for p in range(filas):
        
            pivote = None

            # Va verificando si no hay columnas cero
            if all(matriz[r][p] == 0 for r in range(p, filas)):

                columnaCero = True
                break
            else:

                # Si el elemento de la diagonal es cero, entonces se hace un intercambio de filas
                if matriz[p][p] == 0:

                    for i in range(p + 1, filas):

                        if matriz[i][p] != 0:
                            
                            copia = matriz[i]

                            matriz[i] = matriz[p]
                            matriz[p] = copia

                            print(f"\nSe intercambia la fila {p + 1} con la fila {i + 1}")

                            print("Dado que ocurrió un intercambio de fila, la determinante va a tener el signo opuesto")
                            imprimir_matriz(matriz, log_func=print)
                            det *= -1

                            break

                pivote = matriz[p][p]
                print(f"\nPivote: {pivote:.3f}")
                print(f"Ubicado en la fila {p + 1}, columna {p + 1}")

            det *= pivote
                
            for m in range(p + 1, filas):

                if matriz[m][p] != 0:

                    escalar = matriz[m][p] / pivote

                    for j in range(p, columnas):

                        matriz[m][j] = matriz[m][j] - (matriz[p][j] * escalar)

                    print(f"\nSe elimina la fila {m + 1}, con la fila {p + 1}")
                    imprimir_matriz(matriz, log_func=print)

        if columnaCero:

            print("Se encontró un cero en la diagonal principal")
            print("Por lo tanto, la determinante de la matriz es 0")
            return 0 # Usado para la regla de Cramer
        else:

            print(f"La determinante de la matriz, es igual a: {det}")
            return det # Usado para la regla de Cramer