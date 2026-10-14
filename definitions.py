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

    # Matriz 3x3 -> Dispositivos x Classes + SYSTEM
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
    TOTAL_X = np.sum(X)
        
    return n, np.sum(R, axis=0), X, iterations

n, R, X, iterations = AMVA(system)
print(X * 1000)
print(R / 1000)