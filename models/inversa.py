from models.imprimir_matriz import imprimir_matriz
from copy import deepcopy

def inversaMatriz(matriz, log_func=print):

    """Dada una matriz de n filas, por n columnas, hallar su inversa"""
    
    # Copia de la matriz, para ver si la matriz tiene la misma cantidad de pivotes, que de columnas
    matriz_copia = deepcopy(matriz)
    
    filas = len(matriz_copia)
    columnas = len(matriz_copia[0])

    noHayPivote = False

    # La matriz, debe tener 'n' pivotes
    # Por lo tanto, la matriz tiene que ser obligatoriamente, cuadrada
    if(filas != columnas):

        log_func("No se puede encontrar la inversa a la matriz:")
        imprimir_matriz(matriz_copia, log_func=print)
        log_func("\nDebido a que la matriz debe tener 'n' pivotes, significa que la matriz debe ser cuadrada")
    # Si la matriz es cuadrada, entonces se procede a encontrar si es invertible o no
    else:

        # Se aplica eliminación de Gauss (OJO: No es la de Gauss Jordan)
        log_func("Primero, se verifica si la matriz tiene 'n' pivotes\n")
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

        # Este bloque es ejecuta cuando hay 'n' pivotes
        if not noHayPivote:
            
            log_func("\nPara encontrar la inversa de la matriz, se hace una matriz aumentada ", end="")
            log_func("con la matriz original, más la matriz de identidad, y se procede a aplicar eliminación de Gauss-Jordan\n")

            # Crear matriz identidad
            identidad = [[1 if i == j else 0 for j in range(filas)] for i in range(filas)]

            # Adjuntar matriz identidad a matriz original
            for i in range(filas):
                
                matriz[i] += identidad[i]

            # Eliminación de Gauss Jordan
            log_func("Matriz inicial:\n")
            imprimir_matriz(matriz, log_func=print)

            # Eliminación de filas hacia abajo
            for p in range(filas):
        
                pivote = None

                # Si el elemento de la diagonal es cero, entonces se hace un intercambio de filas
                if matriz[p][p] == 0:

                    for i in range(p + 1, filas):

                        if matriz[i][p] != 0:
                            
                            copia = matriz[i]

                            matriz[i] = matriz[p]
                            matriz[p] = copia

                            log_func(f"\nSe intercambia la fila {p + 1} con la fila {i + 1}")

                            imprimir_matriz(matriz, log_func=print)
                            
                            break

                pivote = matriz[p][p]
                log_func(f"\nPivote: {pivote:.3f}")
                log_func(f"Ubicado en la fila {p + 1}, columna {p + 1}")
            
                for m in range(p + 1, filas):

                    if matriz[m][p] != 0:

                        escalar = matriz[m][p] / pivote

                        for j in range(p, columnas * 2):

                            matriz[m][j] = matriz[m][j] - (matriz[p][j] * escalar)

                        log_func(f"\nSe elimina la fila {m + 1}, con la fila {p + 1}")
                        imprimir_matriz(matriz, log_func=print)

                # Se normaliza la fila. Es decir, que cada elemento se divide entre el pivote 
                for c in range(p, columnas * 2):

                    matriz[p][c] = matriz[p][c] / pivote

                log_func(f"\nSe normaliza la fila {p + 1}")
                imprimir_matriz(matriz, log_func=print)

            # Eliminación de filas hacia arriba
            for r in range(filas - 1, 0, -1):

                pivote = matriz[r][r]
                log_func(f"Pivote: {pivote:.3f}")
                log_func(f"Ubicado en la fila {r + 1}, columna {r + 1}")

                for m in range(r - 1, -1, -1):

                    if matriz[m][r] != 0:

                        escalar = matriz[m][r] / pivote

                        for j in range(r, columnas * 2):

                            matriz[m][j] = matriz[m][j] - (matriz[r][j] * escalar)

                        log_func(f"\nSe elimina la fila {m + 1}, con la fila {r + 1}")
                    
                        imprimir_matriz(matriz, log_func=print)

            # Aquí se imprime la inversa
            inversa = []

            for fila in matriz:

                inversa.append(fila[filas:])

            log_func("\nPor lo tanto, la inversa es igual a:")
            imprimir_matriz(inversa, log_func=print)