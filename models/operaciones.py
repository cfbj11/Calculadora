# Clase para operaciones de matrices: suma y multiplicación

from models.imprimir_matriz import imprimir_matriz

def suma_matrices(A, B, log_func=print):
    """
    Suma A + B mostrando procedimientos.
    """
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ValueError("Error: las matrices deben tener las mismas dimensiones para sumarse.")
    
    filas, cols = len(A), len(A[0])
    R = [[0.0 for _ in range(cols)] for _ in range(filas)]

    for i in range(filas):
        log_func(f"\nFila {i+1}:")
        for j in range(cols):
            proc = f"A[{i+1},{j+1}] + B[{i+1},{j+1}] = {A[i][j]} + {B[i][j]} = {A[i][j] + B[i][j]}"
            log_func(proc)
            R[i][j] = A[i][j] + B[i][j]

    log_func("\nResultado final de la suma:")
    imprimir_matriz(R, "", log_func)
    return R


def multiplicar_matrices(A, B, log_func=print):
    """
    Multiplicación A x B mostrando procedimientos.
    """
    if len(A[0]) != len(B):
        raise ValueError("Error: las dimensiones no son compatibles para la multiplicación (cols A != filas B).")

    filas_A = len(A)
    cols_B = len(B[0])
    k = len(B)  # columnas de A / filas de B
    R = [[0.0 for _ in range(cols_B)] for _ in range(filas_A)]

    for i in range(filas_A):
        log_func(f"\nFila {i+1}:")
        for j in range(cols_B):
            terms = []
            for t in range(k):
                terms.append(f"({A[i][t]})({B[t][j]})")
            expr = " + ".join(terms)

            valores = []
            for t in range(k):
                valores.append(str(A[i][t] * B[t][j]))
            val_expr = " + ".join(valores)

            s = sum(A[i][t] * B[t][j] for t in range(k))
            log_func(f"{expr} = {val_expr} = {s}")
            R[i][j] = s

    log_func("\nResultado final de la multiplicación:")
    imprimir_matriz(R, "", log_func)
    return R
