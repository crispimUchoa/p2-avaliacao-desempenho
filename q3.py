import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

def solve_mixed_network(lambda_Q, lambda_U, D_cpu, D_d1, D_d2, M_I, Z_I):
    # 1. Utilização gerada pelas classes abertas (Q e U)
    U_cpu_open = lambda_Q * D_cpu['Q'] + lambda_U * D_cpu['U']
    U_d1_open  = lambda_Q * D_d1['Q']  + lambda_U * D_d1['U']
    U_d2_open  = lambda_Q * D_d2['Q']  + lambda_U * D_d2['U']

    # Verificação de estabilidade (gargalo não pode exceder 100% de utilização com as classes abertas)
    if max(U_cpu_open, U_d1_open, U_d2_open) >= 1.0:
        return float('inf'), float('inf'), float('inf')

    # 2. Inflacionar os tempos de serviço para a classe fechada (I)
    D_star_cpu = D_cpu['I'] / (1 - U_cpu_open) if D_cpu['I'] > 0 else 0
    D_star_d1  = D_d1['I']  / (1 - U_d1_open)  if D_d1['I'] > 0 else 0
    D_star_d2  = D_d2['I']  / (1 - U_d2_open)  if D_d2['I'] > 0 else 0

    # 3. Algoritmo MVA Exato para a Classe Fechada I
    Q_cpu, Q_d1, Q_d2 = 0.0, 0.0, 0.0
    R_total = 0.0
    X_I = 0.0
    
    for n in range(1, int(M_I) + 1):
        R_cpu = D_star_cpu * (1 + Q_cpu)
        R_d1  = D_star_d1  * (1 + Q_d1)
        R_d2  = D_star_d2  * (1 + Q_d2)

        R_total = R_cpu + R_d1 + R_d2
        X_I = n / (R_total + Z_I)

        Q_cpu = X_I * R_cpu
        Q_d1  = X_I * R_d1
        Q_d2  = X_I * R_d2

    R_I = R_total
    
    # 4. Calcular a utilização total e os tempos de resposta das classes abertas
    U_cpu_total = U_cpu_open + (X_I * D_cpu['I'])
    U_d1_total  = U_d1_open  + (X_I * D_d1['I'])
    U_d2_total  = U_d2_open  + (X_I * D_d2['I'])

    R_Q = (D_cpu['Q'] / (1 - U_cpu_total) + 
           D_d1['Q']  / (1 - U_d1_total) + 
           D_d2['Q']  / (1 - U_d2_total))

    R_U = (D_cpu['U'] / (1 - U_cpu_total) + 
           D_d1['U']  / (1 - U_d1_total) + 
           D_d2['U']  / (1 - U_d2_total))

    return R_Q, R_U, R_I

D_cpu_base = {'Q': 0.06, 'U': 0.10, 'I': 0.09}
D_d1_base  = {'Q': 0.03, 'U': 0.03, 'I': 0.045}
D_d2_base  = {'Q': 0.06, 'U': 0.09, 'I': 0.00}

lambda_Q_base = 3.0
lambda_U_base = 1.5
M_I_base = 50
Z_I = 15

# (a) Tempo de resposta médio para cada classe
R_Q_a, R_U_a, R_I_a = solve_mixed_network(
    lambda_Q_base, lambda_U_base, D_cpu_base, D_d1_base, D_d2_base, M_I_base, Z_I
)

table_a = [
    ["Q", f"{R_Q_a:.4f} s"],
    ["U", f"{R_U_a:.4f} s"],
    ["I", f"{R_I_a:.4f} s"]
]
print("\n(a) Tempos de Resposta Base:")
print(tabulate(table_a, headers=["Classe", "Tempo de Resposta"], tablefmt="grid"))

# (b) Impacto no tempo de resposta com aumento de 95% na taxa de chegada de Q
lambda_Q_novo = lambda_Q_base * 1.95  # 5.85
R_Q_b, R_U_b, R_I_b = solve_mixed_network(
    lambda_Q_novo, lambda_U_base, D_cpu_base, D_d1_base, D_d2_base, M_I_base, Z_I
)

table_b = [
    ["Q", f"{R_Q_b:.4f} s"],
    ["U", f"{R_U_b:.4f} s"],
    ["I", f"{R_I_b:.4f} s"]
]
print(f"\n(b) Tempos de Resposta com lambda_Q = {lambda_Q_novo:.2f}:")
print(tabulate(table_b, headers=["Classe", "Tempo de Resposta"], tablefmt="grid"))

# (c) Comparação de Atualizações de Hardware (com lambda_Q aumentado)
D_d1_upg = {k: v / 2.0 for k, v in D_d1_base.items()}
R_Q_c1, R_U_c1, R_I_c1 = solve_mixed_network(
    lambda_Q_novo, lambda_U_base, D_cpu_base, D_d1_upg, D_d2_base, M_I_base, Z_I
)

D_cpu_upg = {k: v / 2.0 for k, v in D_cpu_base.items()}
R_Q_c2, R_U_c2, R_I_c2 = solve_mixed_network(
    lambda_Q_novo, lambda_U_base, D_cpu_upg, D_d1_base, D_d2_base, M_I_base, Z_I
)

table_c = [
    ["Upgrade D1 (2x mais rápido)", f"{R_Q_c1:.4f} s", f"{R_U_c1:.4f} s", f"{R_I_c1:.4f} s"],
    ["Upgrade CPU (2x mais rápido)", f"{R_Q_c2:.4f} s", f"{R_U_c2:.4f} s", f"{R_I_c2:.4f} s"]
]
print(f"\n(c) Atualizações de Hardware (com lambda_Q={lambda_Q_novo:.2f}):")
print(tabulate(table_c, headers=["Cenário", "R_Q", "R_U", "R_I"], tablefmt="grid"))

# (d) Gráfico e limite máximo de terminais
M_I_range = range(50, 251)
R_I_results = []
max_terminals_1_5s = 0

for m in M_I_range:
    _, _, R_I_val = solve_mixed_network(
        lambda_Q_novo, lambda_U_base, D_cpu_upg, D_d1_base, D_d2_base, m, Z_I
    )
    R_I_results.append(R_I_val)
    
    # Rastrear o número máximo de terminais onde o tempo de resposta se mantém <= 1.5s
    if R_I_val <= 1.5:
        max_terminals_1_5s = m

print(f"\n(d) Número máximo de terminais para manter R_I <= 1.5s: {max_terminals_1_5s}")

# Gerar o Gráfico
plt.figure(figsize=(10, 6))
plt.plot(list(M_I_range), R_I_results, color='b', linewidth=2, label='Tempo de Resposta Interativo (R_I)')
plt.axhline(y=1.5, color='r', linestyle='--', label='Limite de 1.5s')
plt.axvline(x=max_terminals_1_5s, color='g', linestyle=':', label=f'Max Terminais: {max_terminals_1_5s}')

plt.title('Tempo de Resposta vs Número de Terminais\n(CPU 2x mais rápida, lambda_Q = 5.85)')
plt.xlabel('Número de Terminais (M_I)')
plt.ylabel('Tempo de Resposta R_I (segundos)')
plt.legend()
plt.grid(True)
plt.show()