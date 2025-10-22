from models.imprimir_matriz import imprimir_matriz

def detMatriz(matriz, log_func=print):

    filas = len(matriz)
    columnas = len(matriz[0])

    if filas != columnas:

        print("La matriz:")
        imprimir_matriz(matriz)
        print("\nNo es posible sacarle la determinante, debido a que la matriz no es cuadrada")
    else:

        det = 1
        print("Para encontrar la determinante de la matriz, se aplica eliminación de Gauss\n")