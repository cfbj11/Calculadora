from models.vectoresMatrices.eliminacion import eliminacionGaussJordan

def independenciaLineal(conjunto_vectores):

    entradasPorVector = len(conjunto_vectores)
    numeroVectores = len(conjunto_vectores[0])

    # Verifica si sólo se ingresó un solo vector
    if numeroVectores == 1:

        # Si ese vector, es un vector cero, entonces el vector es linealmente dependiente
        if all(conjunto_vectores[x][0] == 0 for x in range(entradasPorVector)):

            print("El vector:")
            imprimirConjunto(conjunto_vectores)
            print("\nEs linealmente dependiente")
            print("Razón: Es un vector cero")
        # Si no es vector cero, entonces el vector es linealmente independiente
        else:

            print("El vector:")
            imprimirConjunto(conjunto_vectores)
            print("\nEs linealmente independiente")
            print("Razón: No es un vector cero")
    # Si hay más vectores que entradas, entonces los vectores son linealmente dependientes
    elif numeroVectores > entradasPorVector:

        print("Los vectores:")
        imprimirConjunto(conjunto_vectores)
        print("\nSon linealmente dependientes")
        print("Razón: La cantidad de vectores, es mayor a la cantidad de entradas que hay en cada vector")
    else:

        vectorCero_existe = False

        for m in range(numeroVectores):

            if all(conjunto_vectores[s][m] == 0 for s in range(entradasPorVector)):

                vectorCero_existe = True
                break

        # Si el vector cero existe, entonces los vectores son linealmente dependientes
        if vectorCero_existe:

            print("Los vectores:")
            imprimirConjunto(conjunto_vectores)
            print("\nSon linealmente dependientes")
            print("Razón: Hay un vector cero")
        # Si no se cumplieron ninguna de las condiciones pasadas, entonces se forma el sistema homogéneo
        else:

            print("Para determinar si el conjunto de vectores es linealmente independiente o no")
            print("Se procede a resolver el sistema homogéneo")
            
            for fila in conjunto_vectores:

                fila.append(0)

            eliminacionGaussJordan(conjunto_vectores)

            dependientes = False
            
            for i in range(numeroVectores):

                # Si se encontra una columna cero, eso quiere decir que sea columna no tiene pivote
                # Por ende, esa columna tendría una variable libre, lo que haría que los vectores sean linealmente dependientes
                if all(conjunto_vectores[j][i] == 0 for j in range(i, entradasPorVector)):

                    dependientes = True

            if dependientes:

                print("\nDebido a que se encontró una variable libre, los vectores son linealmente dependientes")
            else:

                print("\nCómo hay solución única (la cual, es la solución cero), los vectores son linealmente independientes")
                

def imprimirConjunto(vectores):

    for f in range(len(vectores)):

        for c in range(len(vectores[0])):

            print("[", end="")
            print(f"{vectores[f][c]:8.3f}", end="")
            print("  ]", end="")
        
        print("")