# Clase para la eliminacion de filas (Gauss y Gauss-Jordan)

from models.imprimir_matriz import imprimir_matriz

def eliminacionGaussJordan(matriz_a_reducir, log_func=print):


    filas = len(matriz_a_reducir)
    columnas = len(matriz_a_reducir[0])

    variables_libres = []
    columnas_pivote = []
    tieneSolucion = True
    
    # Se imprime la matriz antes de que sea se vuelva en la forma escalonada reducida

    log_func("Matriz inicial:\n")
    imprimir_matriz(matriz_a_reducir, log_func=print)

    # Eliminación de filas hacia abajo
    for p in range(filas):
        
        pivote = None
        
        for c in range(p, columnas):

            # Va verificando si no hay columnas cero
            if all(matriz_a_reducir[r][c] == 0 for r in range(p, filas)):

                continue
            else:

                # Si el elemento de la diagonal es cero, entonces se hace un intercambio de filas
                if matriz_a_reducir[p][c] == 0:

                    for i in range(p + 1, filas):

                        if matriz_a_reducir[i][c] != 0:
                            
                            copia = matriz_a_reducir[i]

                            matriz_a_reducir[i] = matriz_a_reducir[p]
                            matriz_a_reducir[p] = copia

                            log_func(f"\nSe intercambia la fila {p + 1} con la fila {i + 1}")

                            imprimir_matriz(matriz_a_reducir, log_func=print)
                            
                            break

                pivote = matriz_a_reducir[p][c]
                log_func(f"\nPivote: {pivote:.3f}")
                log_func(f"Ubicado en la fila {p + 1}, columna {c + 1}")

                pivote_fi = p
                pivote_col = c
                columnas_pivote.append(c + 1)

                break

        # Si aún así, no se encuentra el pivote, entonces se pasa a la siguiente fila
        if pivote == None:

            print(f"No se encontró pivote en la fila {p + 1}")
            continue
        else:
            
            for m in range(pivote_fi + 1, filas):

                if matriz_a_reducir[m][pivote_col] != 0:

                    escalar = matriz_a_reducir[m][pivote_col] / pivote

                    for j in range(pivote_col, columnas):

                        matriz_a_reducir[m][j] = matriz_a_reducir[m][j] - (matriz_a_reducir[pivote_fi][j] * escalar)

                    log_func(f"\nSe elimina la fila {m + 1}, con la fila {p + 1}")
                    imprimir_matriz(matriz_a_reducir, log_func=print)

            # Se normaliza la fila. Es decir, que cada elemento se divide entre el pivote 
            for c in range(pivote_col, columnas):

                matriz_a_reducir[p][c] = matriz_a_reducir[p][c] / pivote

            log_func(f"\nSe normaliza la fila {p + 1}")
            imprimir_matriz(matriz_a_reducir, log_func=print)

    # Eliminación de filas hacia arriba
    for r in range(filas - 1, 0, -1):

        pivote = None

        for l in range(r, columnas):

            if matriz_a_reducir[r][l] != 0:

                pivote = matriz_a_reducir[r][l]
                log_func(f"Pivote: {pivote:.3f}")
                log_func(f"Ubicado en la fila {r + 1}, columna {l + 1}")

                pivote_fi = r
                pivote_col = l
                break

        if pivote == None:

            log_func(f"No se encontró pivote en la fila {r + 1}")
            continue
        else:
            
            for m in range(pivote_fi - 1, -1, -1):

                if matriz_a_reducir[m][pivote_col] != 0:

                    escalar = matriz_a_reducir[m][pivote_col] / pivote

                    for j in range(pivote_col, columnas):

                        matriz_a_reducir[m][j] = matriz_a_reducir[m][j] - (matriz_a_reducir[pivote_fi][j] * escalar)

                    log_func(f"\nSe elimina la fila {m + 1}, con la fila {p + 1}")
                    
                    imprimir_matriz(matriz_a_reducir, log_func=print)
    
    for f in range(filas):

        # Revisa si no hay filas cero en la matriz de coeficientes
        if all(matriz_a_reducir[f][a] == 0 for a in range(columnas - 1)) and matriz_a_reducir[f][columnas - 1] != 0:

            # Si se encuentra una fila cero en la matriz de coeficientes, entonces el sistema es inconsistente
            tieneSolucion = False
            break

    for v in range(1, columnas):

        try:

            # Si en la columna, el pivote no está presente, entonces es una variable libre
            columnas_pivote.index(v)
        except ValueError:

            variables_libres.append(f"x{v}")
    
    log_func(f"Columnas pivote: {columnas_pivote}")
    
    # Se verifica si la variable 'tieneSolucion' es True o False
    if tieneSolucion:

        # Si no hay variables libres, entonces el sistema tiene solución única
        if variables_libres == []:

            log_func("\nEl sistema tiene una solución única (Consistente)")
            log_func("SOLUCIONES AL SISTEMA:\n")
            
            for s in range(filas):

                try:

                    log_func(f"x{columnas_pivote[s]} = {matriz_a_reducir[s][columnas - 1]:.3f}")
                except IndexError:

                    continue
        # En cambio, si hay variables libres, entonces se muestran aquí
        else:

            log_func("\nEl sistema tiene infinitas soluciones")
            log_func("Variables libres:")
            log_func(variables_libres)
    else:

        log_func("\nEl sistema no tiene solución (Inconsistente)")