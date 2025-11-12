from copy import deepcopy
from fractions import Fraction

from models.determinantes.determinante import detMatriz

def reglaCramer(matriz):

    if len(matriz) + 1 != len(matriz[0]):

        print("No es posible resolver el sistema usando la regla de Cramer")
        print("La cantidad de ecuaciones, debe coincidir con las cantidad de incógnitas")
        print("Para resolver sistemas como estos, utilice Gauss-Jordan o Gauss")
    else:

        print("Primero, se calcula la determinante de la matriz de coeficientes (D)\n")
        matCoeficiente = deepcopy(matriz)
        configurarMatriz(matCoeficiente)
        det_mC = detMatriz(matCoeficiente) # Determinante de la matriz de coeficientes
        print(f"Es decir, D = {det_mC}")

        if det_mC == 0:

            print("\nEntonces, el sistema:")
            print("- Tiene infinitas soluciones")
            print("- Es inconsistente")
        else:

            soluciones = []
            
            print("\nAhora, se definen nuevas matrices, reemplazando la columna i de A, con el vector b")
            # Ciclo que calcula las determinantes
            for m in range(len(matriz)):

                matrizNueva = deepcopy(matriz)
                configurarMatriz(matrizNueva)

                for i in range(len(matriz)):

                    matrizNueva[i][m] = matriz[i][len(matriz[0]) - 1]

                print(f"\nPara la determinante #{m + 1} (D{m + 1})")
                
                det_mN = detMatriz(matrizNueva)
                print(f"O sea, D{m + 1} = {det_mN}")
                soluciones.append(Fraction(det_mN, det_mC))
            
            print("\nPara encontrar las soluciones, se divide las determinantes que se calcularon (D1, D2, ...), entre D respectivamente.")
            print("\nSOLUCIONES DEL SISTEMA:\n")

            for s in range(len(matriz)):

                print(f"x{s + 1} = D{s + 1}/D = {soluciones[s]}")

# Para encontrar la determinantes, se sacan los términos independientes
def configurarMatriz(mat_configurar):

    for fila in mat_configurar:

        fila.pop()