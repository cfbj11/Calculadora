from models.imprimir_matriz import imprimir_matriz

def transpuestamatriz(matriz):

    transpuesta = []
    
    filas = len(matriz[0])
    columnas = len(matriz)

    for n in range(filas):

        transpuesta.append(list())

        for m in range(columnas):

            transpuesta[n].append(matriz[m][n])

    print("\nLa transpuesta de la matriz sería")
    imprimir_matriz(transpuesta, log_func=print)

    if transpuesta == matriz:

        print("\nAdemás, la matriz es simétrica")
        print("O sea, su transpuesta es igual a ella misma")

    # Retorna el resultado (utilizado en la suma y en la multiplicación como opciones)
    return transpuesta