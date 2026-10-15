from typing import TypedDict
from copy import deepcopy
import numpy as np

STOP_CONDITION = 0.001

QUERY = 0
UPDATE = 1
SYSTEM = 2

CPU = 0
DISK_1 = 1
DISK_2 = 2

DEVICES = [CPU, DISK_1, DISK_2]

CLASSES = [QUERY, UPDATE]

# Demanda em ms
class Demand(TypedDict):
    CPU: int
    DISK_1: int
    DISK_2: int
    

class SysClass(TypedDict):
    demand: Demand
    #multiprograming level
    mpl: int
    # transactions completed
    c: int 
    # monitoring period in ms
    monitoring_period: int


class System:
    classes: list[SysClass]
    mpl: int
    queue_length: np.typing.ArrayLike
    def __init__(self, classes: list[SysClass]):
        self.classes = classes
        self.mpl = sum([c['mpl'] for c in classes])
        self.queue_length = np.zeros((3, 3))


    def __str__(self):

        return f'CLASSES: {self.classes}\nMPL: {self.mpl}'


query_class: SysClass = {
    'demand': {CPU: 105, DISK_1: 180, DISK_2: 0},
    'c':7368,
    'monitoring_period': 1800 * 1000,
    'mpl': 3
    }

update_class: SysClass = {
    'demand': {CPU: 375, DISK_1: 480, DISK_2: 240},
    'c': 736,
    'monitoring_period': 1800 * 1000,
    'mpl': 1
}





system = System([query_class, update_class])

def get_max_diff(system: System, nnew):
    nold = system.queue_length
    diffs = nold[:, len(CLASSES)] - nnew[:, len(CLASSES)]

    max = np.abs(diffs).max()

    return max

def AMVA(system: System):
    n = np.copy(system.queue_length)
    for CLASS in CLASSES:
        q_len = system.classes[CLASS]['mpl'] / len(DEVICES)
        n[CPU][CLASS] = q_len
        n[DISK_1][CLASS] = q_len
        n[DISK_2][CLASS] = q_len

    for DEVICE in DEVICES:
        n[DEVICE][SYSTEM] = n[DEVICE][QUERY] + n[DEVICE][UPDATE]

    R = np.zeros((3, 2))
    X = np.zeros(2)
    iterations = 0
    
    while (get_max_diff(system, n) > STOP_CONDITION):
        iterations +=1
        for CLASS in CLASSES:
            sys_class = system.classes[CLASS]
            for DEVICE in DEVICES:
                R[DEVICE][CLASS] = sys_class['demand'][DEVICE] * (1 + n[DEVICE][SYSTEM] - n[DEVICE][CLASS]/sys_class['mpl'])

            X[CLASS] = sys_class['mpl']/np.sum(R[:, CLASS])
            system.queue_length = np.copy(n)
            for DEVICE in DEVICES:
                n[DEVICE][CLASS] = X[CLASS] * R[DEVICE][CLASS]

        for DEVICE in DEVICES:
                n[DEVICE][SYSTEM] = n[DEVICE][QUERY] + n[DEVICE][UPDATE]


    system.queue_length = n
        
    return n, np.sum(R, axis=0), X, iterations

import numpy as np

def MVA(system):
    QUERY_MPL = system.classes[QUERY]['mpl']
    UPDATE_MPL = system.classes[UPDATE]['mpl']
    
    # Arrays indexados por: [Dispositivo, Classe, i, j]
    # Tamanho +1 para incluir as populações de 0 até MPL
    n_total = np.zeros((len(DEVICES), QUERY_MPL + 1, UPDATE_MPL + 1))
    R = np.zeros((len(DEVICES), len(CLASSES), QUERY_MPL + 1, UPDATE_MPL + 1))
    X = np.zeros((len(CLASSES), QUERY_MPL + 1, UPDATE_MPL + 1))

    for i in range(QUERY_MPL + 1):
        for j in range(UPDATE_MPL + 1):
            if i == 0 and j == 0:
                continue
            
            pop = [i, j]
            
            # 1. Calcular Tempo de Resposta (R)
            for c in CLASSES:
                if pop[c] == 0:
                    continue  # Pula se a classe não tem clientes neste estado
                
                # Vetor unitario e_r: subtrai 1 da classe c
                e = [0, 0]
                e[c] = 1
                
                prev_i = i - e[0]
                prev_j = j - e[1]
                
                for dev in DEVICES:
                    demand = system.classes[c]['demand'][dev]
                    # Fila do dispositivo 'dev' com 1 cliente a menos da classe 'c'
                    prev_n = n_total[dev, prev_i, prev_j]
                    R[dev, c, i, j] = demand * (1 + prev_n)
            
            # 2. Calcular Vazão Global (X)
            for c in CLASSES:
                if pop[c] == 0:
                    continue
                sum_R = np.sum(R[:, c, i, j])
                X[c, i, j] = pop[c] / sum_R
            
            # 3. Atualizar Fila Média Total por Dispositivo n_i(i, j)
            for dev in DEVICES:
                n_total[dev, i, j] = sum(X[c, i, j] * R[dev, c, i, j] for c in CLASSES)

    return np.sum(R[:, :, QUERY_MPL, UPDATE_MPL], axis=0), X[:, QUERY_MPL, UPDATE_MPL], n_total[:, QUERY_MPL, UPDATE_MPL]

n, R, X, iterations = AMVA(deepcopy(system))
# print(X * 1000)
# print(R / 1000)

R, X, n_total = MVA(system)

print(f'{R=}')
print(f'{X=}')
print(f'{n_total=}')