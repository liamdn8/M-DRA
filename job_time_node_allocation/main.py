import cvxpy as cp
import numpy as np
import pandas as pd
from tabulate import tabulate

# -----------------------
# 1) Problem dimensions (swapped)
# -----------------------
N = 3  # number of clusters
M = 10 # number of jobs
K = 4  # number of worker nodes
T = 4  # number of time slices

# -----------------------
# 2) Input data
# -----------------------
# Job memory requirement
w = [9, 6, 8, 4, 6, 8, 4, 6, 8, 8]  # Memory demand for jobs j=0..M-1

# Job duration
d = [2, 2, 1, 1, 3, 1, 2, 3, 2, 3]  # Memory demand for jobs j=0..M-1

# Node memory capacities
s = [20, 24, 20, 24]  # Memory capacity for nodes k=0..K-1

# c[j][i] = 1 if job j can be scheduled to run on cluster i, else 0
c = [
    [1, 1, 1],  # job 0 can be scheduled on cluster 0, 1
    [1, 1, 1],  # job 0 can be scheduled on cluster 0, 1
    [1, 1, 1],  # job 0 can be scheduled on cluster 0, 1
    [1, 1, 0],  # job 0 can be scheduled on cluster 0, 1
    [1, 1, 0],  # job 0 can be scheduled on cluster 0, 1
    [0, 1, 1],  # job 0 can be scheduled on cluster 0, 1
    [0, 1, 1],  # job 0 can be scheduled on cluster 0, 1
    [0, 0, 1],  # job 0 can be scheduled on cluster 0, 1
    [0, 0, 1],  # job 0 can be scheduled on cluster 0, 1
    [0, 0, 1],  # job 0 can be scheduled on cluster 0, 1
    [0, 0, 1],  # job 0 can be scheduled on cluster 0, 1
]


# ------------------------------------------------------
# 3) Decision variables:
# ------------------------------------------------------
# x[i,k,t] = 1 if node k is attached to cluster i at time t
x = cp.Variable((N, K, T), boolean=True)

# y[j,i] = 1 if job j be scheduled to run on cluster i
y = cp.Variable((M, N), boolean=True)

# z[j,t] = 1 if job j be started to run at time slice t
z = cp.Variable((M, T), boolean=True)

# Calculate a_jt
a = cp.Variable((M, T), boolean=True)

# Job started time started_j: the time slice index that job start
job_start = cp.Variable((M), integer=True)
earliest_job_start = cp.Variable(integer=True)

# Job finished time finished_j: the time slice index that job finished
job_end = cp.Variable((M), integer=True)
latest_job_end = cp.Variable(integer=True)
        
# -----------------------
# 4) Constraints
# -----------------------
constraints = []

# (A) Job scheduling constraint
for j_ in range(M):
    # A job must be scheduled on exactly one cluster
    constraints.append( cp.sum(y[j_,:])==1 ) 

    # A job must be started exactly once
    constraints.append( cp.sum(z[j_,:])==1 ) 

    # Job must run without interruption
    for t_ in range(T):
        constraints.append(a[j_,t_] == cp.sum(z[j_, max(0, t_ - d[j_] + 1):t_]))
        
    # Job must be completed
    constraints.append( d[j_]==sum(a[j_,t_] for t_ in range (T))) 



# (B) Node allocation constraint: each worker node k must be assigned to exactly one cluster i at each time t
for k_ in range(K):
    for t_ in range(T):
        constraints.append(cp.sum(x[:, k_, t_]) == 1)

# (C) CPU capacity per cluster i at time t
for i_ in range(N):
    for t_ in range(T):
        # Total CPU demand for jobs assigned to cluster i_ at time t
        cpu_demand = sum(a[j_][t_] * w[j_] * y[j_][i_] for j_ in range(M))
        # Total CPU capacity from nodes assigned to cluster i_ at time t
        cpu_capacity = cp.sum([s[k_] * x[i_, k_, t_] for k_ in range(K)])

        constraints.append(cpu_demand <= cpu_capacity)

# (D) Link job start/finish time
for j_ in range (M):
    # job_start[j] = ∑ t·z[j,t]
    constraints.append(job_start[j_] == cp.sum(cp.multiply(np.arange(T), z[j_,:])))
    # job_end[j] = job_start[j] + d[j] - 1
    constraints.append(job_end[j_] == job_start[j_] + d[j_] - 1)
    
    # earliest job start:
    constraints.append(earliest_job_start <= job_start[j_])
    # lastest job finish:
    constraints.append(latest_job_end >= job_end[j_])

# (E) Time slice limit
# job not start before time slice 0
constraints.append(earliest_job_start >= 0)
# job not end after time slice T-1
constraints.append(latest_job_end <= T-1)


# -----------------------
# 5) Objective
# -----------------------
# Makespan

objective = cp.Minimize(latest_job_end - earliest_job_start)

# -----------------------
# 6) Solve
# -----------------------
problem = cp.Problem(objective, constraints)
result = problem.solve(solver=cp.GLPK_MI)

# -----------------------
# 7) Print results
# -----------------------
print("Solver status:", problem.status)
print("Optimal objective value (relocations):", problem.value)


if problem.status == cp.OPTIMAL and x.value is not None:
    print("Status:", problem.status)
    print("Window length:", problem.value)
    print("Earliest start:", earliest_job_start.value)
    print("Latest finish:", latest_job_end.value)

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
                "Mem Capacity": mem_cap,
                "Mem Usage": mem_usage
            })
            table.append(cluster_table)

#     for i_ in range(N):
#         df = pd.DataFrame(table[i_])
#         print(f"\nSummary Table for Cluster {i_}:")
#         # Using tabulate to pretty-print the DataFrame as a table.
#         print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))


else:
    print("No optimal solution found. Problem status:", problem.status)
