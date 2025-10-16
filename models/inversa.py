from models.imprimir_matriz import imprimir_matriz
from copy import deepcopy

def inversaMatriz(matriz, log_func=print):

    """Dada una matriz de n filas, por n columnas, hallar su inversa"""
    
    # Copia de la matriz, para ver si
    matriz_copia = deepcopy(matriz)
    
    filas = len(matriz_copia)
    columnas = len(matriz_copia[0])

    columnas_pivote = []

    noHayPivote = False

    # La matriz, debe tener 'n' pivotes
    # Por lo tanto, la matriz tiene que ser obligatoriamente, cuadrada
    if(filas != columnas):

        log_func("No se puede encontrar la inversa a la matriz:")
        imprimir_matriz(matriz_copia, log_func=print)
        log_func("\nDebido a que la matriz debe tener 'n' pivotes, significa que la matriz debe ser cuadrada")
    # Si la matriz es cuadrada, entonces se procede a encontrar si es invertible o no
    else:

        log_func("Matriz inicial:\n")
        imprimir_matriz(matriz_copia, log_func=print)

        # Eliminación de filas hacia abajo
        for p in range(filas):
        
            pivote = None
        
            for c in range(p, columnas):

                # Va verificando si no hay columnas cero
                if all(matriz_copia[r][c] == 0 for r in range(p, filas)):

                    noHayPivote = True
                    break
                else:

                    # Si el elemento de la diagonal es cero, entonces se hace un intercambio de filas
                    if matriz_copia[p][c] == 0:

                        for i in range(p + 1, filas):

                            if matriz_copia[i][c] != 0:
                            
                                copia = matriz_copia[i]

                                matriz_copia[i] = matriz_copia[p]
                                matriz_copia[p] = copia

                                log_func(f"\nSe intercambia la fila {p + 1} con la fila {i + 1}")

                                imprimir_matriz(matriz_copia, log_func=print)
                            
                                break

                    pivote = matriz_copia[p][c]
                    log_func(f"\nPivote: {pivote:.3f}")
                    log_func(f"Ubicado en la fila {p + 1}, columna {c + 1}")

                    pivote_fi = p
                    pivote_col = c
                    columnas_pivote.append(c + 1)

                    break
            
            if noHayPivote:

                log_func("\nSe encontró una columna que no tiene pivote")
                log_func("Por lo tanto, la matriz no es invertible")
                break
            else:
            
                for m in range(pivote_fi + 1, filas):

                    if matriz_copia[m][pivote_col] != 0:

                        escalar = matriz_copia[m][pivote_col] / pivote

                        for j in range(pivote_col, columnas):

                            matriz_copia[m][j] = matriz_copia[m][j] - (matriz_copia[pivote_fi][j] * escalar)

                        log_func(f"\nSe elimina la fila {m + 1}, con la fila {p + 1}")
                        imprimir_matriz(matriz_copia, log_func=print)

        imprimir_matriz(matriz, log_func=print)