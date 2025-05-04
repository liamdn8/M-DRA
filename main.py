import cvxpy as cp
import numpy as np
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import os

# -----------------------
# 1) Problem dimensions
# -----------------------
N = 3   # number of clusters
M = 10  # number of jobs
K = 4   # number of worker nodes
T = 4   # number of time slices

# -----------------------
# 2) Input data
# -----------------------
w = [9, 6, 8, 4, 6, 8, 4, 6, 8, 8]      # Memory demand for jobs j=0..M-1
d = [2, 2, 1, 1, 3, 1, 2, 3, 2, 3]      # Duration for jobs j=0..M-1
s = [20, 24, 20, 24]                    # Memory capacity for nodes k=0..K-1
c = np.array([                           # c[j,i] = 1 if job j runs on cluster i
    [1, 0, 0],  # jobs 0..4 → cluster 0
    [1, 0, 0],
    [1, 0, 0],
    [1, 0, 0],
    [1, 0, 0],
    [0, 1, 0],  # jobs 5..7 → cluster 1
    [0, 1, 0],
    [0, 1, 0],
    [0, 0, 1],  # jobs 8..9 → cluster 2
    [0, 0, 1],
])

# -----------------------
# 3) Decision variables
# -----------------------
x = cp.Variable((N, K, T), boolean=True)
# y[j,t] =1 if job j *starts* at timeslice t
y = cp.Variable((M, T), boolean=True)
# start and end times
job_start = cp.Variable(M, integer=True)
job_end   = cp.Variable(M, integer=True)
earest_start = cp.Variable(integer=True)
latest_end   = cp.Variable(integer=True)

# -----------------------
# 4) Constraints
# -----------------------
cons = []

# (A) Each job starts exactly once and within horizon
for j in range(M):
    cons.append(cp.sum(y[j, :]) == 1)
    # prevent overruns
    for t in range(T - d[j] + 1, T):
        cons.append(y[j, t] == 0)

# (B) Node allocation: each node must belong to exactly one cluster per slice
for k in range(K):
    for t in range(T):
        cons.append(cp.sum(x[:, k, t]) == 1)

# (C) Memory capacity per cluster/time
for i in range(N):
    for t in range(T):
        # sum of demands of jobs active at t on cluster i
        mem_req = 0
        for j in range(M):
            # job j active at t if started in [t-d[j]+1 .. t]
            for tau in range(max(0, t - d[j] + 1), t + 1):
                mem_req += w[j] * c[j, i] * y[j, tau]
        # available memory
        mem_cap = sum(s[k] * x[i, k, t] for k in range(K))
        cons.append(mem_req <= mem_cap)

# (D) Link start/end and makespan bounds
for j in range(M):
    # start = sum t*y[j,t]
    cons.append(job_start[j] == cp.sum(cp.multiply(np.arange(T), y[j, :])))
    # end = start + duration -1
    cons.append(job_end[j] == job_start[j] + d[j] - 1)
    # track global earliest/latest
    cons.append(earest_start <= job_start[j])
    cons.append(latest_end   >= job_end[j])

# enforce bounds
cons.append(earest_start >= 0)
cons.append(latest_end <= T - 1)

# -----------------------
# 5) Objective: minimize makespan
# -----------------------
obj = cp.Minimize(latest_end - earest_start)
prob = cp.Problem(obj, cons)
prob.solve(solver=cp.GLPK_MI)

# -----------------------
# 6) Print summary
# -----------------------
print(f"Solver status: {prob.status}")
if prob.status == cp.OPTIMAL:
    print(f"Optimal makespan = {prob.value}\n")
    print("Job | Start | End")
    print("----+-------+-----")
    for j in range(M):
        print(f" {j:>2} |  {job_start.value[j]:>2}   | {job_end.value[j]:>2}")

# -----------------------
# 7) Plot per-cluster Gantt charts
# -----------------------
if prob.status == cp.OPTIMAL:
    out_dir = "plots"
    os.makedirs(out_dir, exist_ok=True)

    for i in range(N):
        # select jobs assigned to cluster i
        jobs_i = [j for j in range(M) if c[j, i] == 1]
        if not jobs_i:
            continue
        fig, ax = plt.subplots()
        starts = [job_start.value[j] for j in jobs_i]
        ends   = [job_end.value[j]   for j in jobs_i]
        durations = [ends[k] - starts[k] + 1 for k in range(len(jobs_i))]

        ax.barh(jobs_i, durations, left=starts)
        ax.set_yticks(jobs_i)
        ax.set_ylabel('Job ID')
        ax.set_xlabel('Time slice')
        ax.set_title(f'Cluster {i} schedule')
        plt.tight_layout()

        fname = os.path.join(out_dir, f"cluster_{i}.png")
        plt.savefig(fname)
        print(f"Saved cluster {i} plot to {fname}")
        plt.close(fig)
