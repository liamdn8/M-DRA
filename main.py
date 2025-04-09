import cvxpy as cp
import numpy as np
import pandas as pd
from tabulate import tabulate

# -----------------------
# 1) Problem dimensions (swapped)
# -----------------------
N = 2  # number of clusters
M = 10 # number of jobs
K = 4  # number of worker nodes
T = 4  # number of time slices

# -----------------------
# 2) Input data
# -----------------------
# CPU and memory demands of each job
c = [4, 3, 4, 5, 6, 2, 3, 4, 5, 6]  # CPU demand for jobs j=0..1
e = [9, 6, 8, 4, 6, 8, 4, 6, 8, 8]  # Memory demand for jobs j=0..1

# Node capacities (CPU and memory)
r = [10, 10, 10, 10]  # CPU capacity for nodes k=0..1
s = [20, 24, 20, 24]  # Memory capacity for nodes k=0..1

# g[j][t] = 1 if job j is active at time t, else 0
g = [
    [1, 1, 0, 0],  # job 0 active at times t=0,1
    [1, 1, 0, 0],  # job 1 active at times t=0,1
    [0, 1, 1, 0],  # job 2 active at times t=1,2
    [0, 1, 1, 1],  # job 3 active at times t=2,3
    [0, 1, 1, 0],  # job 4 active at times t=1,2
    [0, 1, 1, 1],  # job 5 active at times t=1,2,3
    [1, 1, 1, 0],  # job 6 active at times t=0,1
    [0, 0, 1, 0],  # job 7 active at times t=2
    [0, 0, 1, 1],  # job 8 active at times t=2,3
    [0, 1, 1, 1],  # job 9 active at times t=1,2,3
]

# h[j][i] = 1 if job j is assigned to cluster i, else 0
# Now, i ranges over clusters (i = 0,..,N-1)
h = [
    [1, 0],  # job 0 assigned to cluster 0
    [1, 0],  # job 1 assigned to cluster 0
    [1, 0],  # job 2 assigned to cluster 0
    [1, 0],  # job 3 assigned to cluster 0
    [1, 0],  # job 4 assigned to cluster 0
    [1, 0],  # job 5 assigned to cluster 0
    [0, 1],  # job 6 assigned to cluster 1
    [0, 1],  # job 7 assigned to cluster 1
    [0, 1],  # job 8 assigned to cluster 1
    [0, 1],  # job 9 assigned to cluster 1
]

# ------------------------------------------------------
# 3) Decision variables: x[i,k,t] and relocation helpers
# ------------------------------------------------------
# x[i,k,t] = 1 if node k is attached to cluster i at time t
# Here, i indexes clusters (0 to N-1) and k indexes worker nodes (0 to K-1)
x = cp.Variable((N, K, T), boolean=True)

# -----------------------
# 4) Constraints
# -----------------------
constraints = []

# (A) Node allocation: each worker node k must be assigned to exactly one cluster i at each time t
for k_ in range(K):
    for t_ in range(T):
        constraints.append(cp.sum(x[:, k_, t_]) == 1)

# (B) CPU capacity per cluster i at time t
for i_ in range(N):
    for t_ in range(T):
        # Total CPU demand for jobs assigned to cluster i_ at time t
        cpu_demand = sum(c[j_] * g[j_][t_] * h[j_][i_] for j_ in range(M))
        # Total CPU capacity from nodes assigned to cluster i_ at time t
        cpu_capacity = cp.sum([r[k_] * x[i_, k_, t_] for k_ in range(K)])
        constraints.append(cpu_demand <= cpu_capacity)

# (C) Memory capacity per cluster i at time t
for i_ in range(N):
    for t_ in range(T):
        mem_demand = sum(e[j_] * g[j_][t_] * h[j_][i_] for j_ in range(M))
        mem_capacity = cp.sum([s[k_] * x[i_, k_, t_] for k_ in range(K)])
        constraints.append(mem_demand <= mem_capacity)

# -----------------------
# 5) Objective
# -----------------------
# We sum up d[i,k,t] and multiply by 0.5 to count one relocation per change.
# obj = 0
# for i_ in range(N):
#     for k_ in range(K):
#         for t_ in range(T-1):
#             obj += d[i_, k_, t_]

obj = sum(
        sum(
            sum(cp.abs(x[i_, k_, t_] - x[i_, k_, t_-1]) for t_ in range(1, T) )
            for k_ in range(K))
        for i_ in range(N))

objective = cp.Minimize(0.5 * obj)

# -----------------------
# 6) Solve
# -----------------------
problem = cp.Problem(objective, constraints)
result = problem.solve()

# -----------------------
# 7) Print results
# -----------------------
print("Solver status:", problem.status)
print("Optimal objective value (relocations):", problem.value)


if problem.status == cp.OPTIMAL and x.value is not None:
    # x[i,k,t] solution: now i indexes clusters and k indexes worker nodes
    x_sol = np.abs(x.value)

    table = []
    for t_ in range(T):
        print("-----------------------")
        print(f"Time slice t={t_}")
        print("-----------------------")

        for k_ in range(K):
            assigned_cluster = np.argmax(x_sol[:, k_, t_])
            print(f"  Worker Node {k_} -> Cluster {assigned_cluster} (x={x_sol[:, k_, t_]})")

        for i_ in range (N):
            cpu_usage = sum(c[j_] * g[j_][t_] * h[j_][i_] for j_ in range(M))
            mem_usage = sum(e[j_] * g[j_][t_] * h[j_][i_] for j_ in range(M))
            cpu_cap = cp.sum([r[k_] * x[i_, k_, t_] for k_ in range(K)]).value
            mem_cap = cp.sum([s[k_] * x[i_, k_, t_] for k_ in range(K)]).value

            cluster_table = []
            cluster_table.append({
                "Time Slice": t_,
                "Cluster": i_,
                "CPU Capacity": cpu_cap,
                "Mem Capacity": mem_cap,
                "CPU Usage": cpu_usage,
                "Mem Usage": mem_usage
            })
            table.append(cluster_table)

    for i_ in range(N):
        df = pd.DataFrame(table[i_])
        print(f"\nSummary Table for Cluster {i_}:")
        # Using tabulate to pretty-print the DataFrame as a table.
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))


else:
    print("No optimal solution found. Problem status:", problem.status)
