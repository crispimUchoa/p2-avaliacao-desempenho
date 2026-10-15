from definitions import query_class, update_class, deepcopy, print_table, System, MVA, DISK_1, DISK_2, MVA_PE

query_balanced = deepcopy(query_class)
query_balanced['demand'][DISK_1] = query_balanced['demand'][DISK_1] / 2 
query_balanced['demand'][DISK_2] = query_balanced['demand'][DISK_1] 

mva = MVA(System([query_balanced, update_class]))

mva_std = MVA(System([query_class, update_class]))

print_table(mva, "MVA - QUERY BALANCED")

diff = MVA_PE(mva, mva_std)

print_table(diff, "DIFF (NEW_MVA - OLD_MVA)/OLD_MVA (%)", show_unity=False)