import cvxpy as cp
import numpy as np

# -----------------------
# 1) Problem dimensions (swapped)
# -----------------------
N = 2  # number of clusters
K = 2  # number of worker nodes
M = 2  # number of jobs
T = 4  # number of time slices

# -----------------------
# 2) Input data
# -----------------------
# CPU and memory demands of each job
c = [2, 3]  # CPU demand for jobs j=0..1
e = [4, 2]  # Memory demand for jobs j=0..1

# Node capacities (CPU and memory)
r = [4, 4]  # CPU capacity for nodes k=0..1
s = [6, 6]  # Memory capacity for nodes k=0..1

# G[j][t] = 1 if job j is active at time t, else 0
G = [
    [1, 1, 0, 0],  # job 0 active at times t=0,1
    [0, 1, 1, 0],  # job 1 active at times t=1,2
]

# h[j][i] = 1 if job j is assigned to cluster i, else 0
# Now, i ranges over clusters (i = 0,..,N-1)
h = [
    [1, 0],  # job 0 assigned to cluster 0
    [0, 1],  # job 1 assigned to cluster 1
]

# ------------------------------------------------------
# 3) Decision variables: x[i,k,t] and relocation helpers
# ------------------------------------------------------
# x[i,k,t] = 1 if node k is attached to cluster i at time t
# Here, i indexes clusters (0 to N-1) and k indexes worker nodes (0 to K-1)
x = cp.Variable((N, K, T), boolean=True)

# d[i,k,t] >= 0 to capture |x[i,k,t] - x[i,k,t-1]|
# Defined for time slices t=1,..,T-1 (T-1 "gaps").
d = cp.Variable((N, K, T-1), nonneg=True)

constraints = []

# -----------------------
# 4) Constraints
# -----------------------

# (A) Node allocation: each worker node k must be assigned to exactly one cluster i at each time t
for k_ in range(K):
    for t_ in range(T):
        constraints.append(cp.sum(x[:, k_, t_]) == 1)

# (B) CPU capacity per cluster i at time t
for i_ in range(N):
    for t_ in range(T):
        # Total CPU demand for jobs assigned to cluster i_ at time t
        cpu_demand = sum(c[j_] * G[j_][t_] * h[j_][i_] for j_ in range(M))
        # Total CPU capacity from nodes assigned to cluster i_ at time t
        cpu_capacity = cp.sum([r[k_] * x[i_, k_, t_] for k_ in range(K)])
        constraints.append(cpu_demand <= cpu_capacity)

# (C) Memory capacity per cluster i at time t
for i_ in range(N):
    for t_ in range(T):
        mem_demand = sum(e[j_] * G[j_][t_] * h[j_][i_] for j_ in range(M))
        mem_capacity = cp.sum([s[k_] * x[i_, k_, t_] for k_ in range(K)])
        constraints.append(mem_demand <= mem_capacity)

# (D) Relocation constraints: linearize |x[i,k,t] - x[i,k,t-1]|
for i_ in range(N):
    for k_ in range(K):
        for t_ in range(1, T):
            constraints.append(d[i_, k_, t_-1] >= x[i_, k_, t_] - x[i_, k_, t_-1])
            constraints.append(d[i_, k_, t_-1] >= x[i_, k_, t_-1] - x[i_, k_, t_])

# -----------------------
# 5) Objective
# -----------------------
# We sum up d[i,k,t] and multiply by 0.5 to count one relocation per change.
obj = 0
for i_ in range(N):
    for k_ in range(K):
        for t_ in range(T-1):
            obj += d[i_, k_, t_]

objective = cp.Minimize(0.5 * obj)

# -----------------------
# 6) Solve
# -----------------------
problem = cp.Problem(objective, constraints)
result = problem.solve(
)

# -----------------------
# 7) Print results
# -----------------------
print("Solver status:", problem.status)
print("Optimal objective value (relocations):", problem.value)

# x[i,k,t] solution: now i indexes clusters and k indexes worker nodes
x_sol = x.value
print("\nNode-to-Cluster Assignments (x):")
for t_ in range(T):
    print(f"Time slice t={t_}:")
    for k_ in range(K):
        assigned_cluster = np.argmax(x_sol[:, k_, t_])
        print(f"  Worker Node {k_} -> Cluster {assigned_cluster} (x={x_sol[:, k_, t_]})")

