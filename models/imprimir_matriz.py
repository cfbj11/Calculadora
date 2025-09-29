# Clase para imprimir matrices

def imprimir_matriz(matriz, log_func=print):
    """
    Imprime una matriz con formato legible.
    `log_func` permite enviar la salida a consola o a la UI (Text widget).
    """

    # Imprime cada fila de la matriz
    for fila in matriz:
        try:
            line = "  ".join(f"{x:8.3f}" for x in fila)
        except Exception:
            # En caso de datos no numéricos, imprimir tal cual
            line = "  ".join(str(x) for x in fila)
        log_func(line)
    log_func("")  # línea en blanco