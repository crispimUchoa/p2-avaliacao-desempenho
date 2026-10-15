from definitions import MVA, AMVA, print_table, System, query_class, update_class, deepcopy, np, MVA_APE

amva = AMVA(System([query_class, update_class]))
print("------------------- CASO BASE -------------------\n")

print_table(amva, "AMVA - APROXIMADO")

mva = MVA(System([query_class, update_class]))

print_table(mva, "MVA - EXATO")

print('\n')

query_class_3 = deepcopy(query_class)
update_class_3 = deepcopy(update_class)
query_class_3['mpl'] = 1
update_class_3['mpl'] = 3


mva_ape = MVA_APE(amva, mva)
print_table(mva_ape, "ABSOLUTE ERROR (%)", show_unity=False)

print("------------------- CASO COM UPDATE CLASS MPL = 3 -------------------\n")

amva = AMVA(System([query_class_3, update_class_3]))
print_table(amva, "AMVA - APROXIMADO")

mva = MVA(System([query_class_3, update_class_3]))

print_table(mva, "MVA - EXATO")

mva_ape = MVA_APE(amva, mva)
print_table(mva_ape, "ABSOLUTE ERROR (%)", show_unity=False)
