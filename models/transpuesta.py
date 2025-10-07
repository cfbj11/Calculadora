from models.imprimir_matriz import imprimir_matriz

def transpuestamatriz(matriz, log_func=print):

    transpuesta = []
    
    filas = len(matriz[0])
    columnas = len(matriz)

    for n in range(filas):

        transpuesta.append(list())

        for m in range(columnas):

            transpuesta[n].append(matriz[m][n])

    log_func("\nLa transpuesta de la matriz sería")
    imprimir_matriz(transpuesta, log_func=print)

    if transpuesta == matriz:

        log_func("\nAdemás, la matriz es simétrica")
        log_func("O sea, su transpuesta es igual a ella misma")