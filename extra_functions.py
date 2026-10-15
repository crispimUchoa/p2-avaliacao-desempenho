import numpy as np


def mva_tuple_to_matrix(mva_tuple, shape=(4, 3)):
    """
    Converte a tupla de retornos do MVA/AMVA em uma única matriz 4x3.
    Cada elemento da tupla vira uma linha, e linhas menores são preenchidas com 0.
    """
    matriz = np.zeros(shape)
    
    for i, arr in enumerate(mva_tuple):
        arr_1d = np.asarray(arr).ravel()  # Garante vetor 1D
        tamanho = min(len(arr_1d), shape[1])
        matriz[i, :tamanho] = arr_1d[:tamanho]
        
    return matriz