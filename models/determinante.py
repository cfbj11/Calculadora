from models.imprimir_matriz import imprimir_matriz

def detMatriz(matriz, log_func=print):

    filas = len(matriz)
    columnas = len(matriz[0])

    columnaCero = False

    if filas != columnas:

        print("La matriz:")
        imprimir_matriz(matriz)
        print("\nNo es posible sacarle la determinante, debido a que la matriz no es cuadrada")
    else:

        det = 1 # Se inicializa con el valor de '1', para multiplicar por '-1', en caso de que hay intercambio de fila
        log_func("Primero, se aplica eliminación de Gauss, para reducirla a la matriz triangular superior")
        log_func("Para calcular la determinante, se multiplica cada elemento de la diagonal principal")
        log_func("Si hay un cero, entonces la determinante es 0")

        log_func("Matriz inicial:\n")
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

                            log_func(f"\nSe intercambia la fila {p + 1} con la fila {i + 1}")

                            log_func("Dado que ocurrió un intercambio de fila, la determinante va a tener el signo opuesto")
                            imprimir_matriz(matriz, log_func=print)
                            det *= -1

                            break

                pivote = matriz[p][p]
                log_func(f"\nPivote: {pivote:.3f}")
                log_func(f"Ubicado en la fila {p + 1}, columna {p + 1}")

            det *= pivote
                
            for m in range(p + 1, filas):

                if matriz[m][p] != 0:

                    escalar = matriz[m][p] / pivote

                    for j in range(p, columnas):

                        matriz[m][j] = matriz[m][j] - (matriz[p][j] * escalar)

                    log_func(f"\nSe elimina la fila {m + 1}, con la fila {p + 1}")
                    imprimir_matriz(matriz, log_func=print)

        if columnaCero:

            log_func("Se encontró un cero en la diagonal principal")
            log_func("Por lo tanto, la determinante de la matriz es: 0")
        else:

            log_func(f"La determinante de la matriz, es igual a: {det}")