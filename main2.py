import cvxpy as cp
import numpy as np
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
y = cp.Variable((M, T), boolean=True)  # y[j,t] =1 if job j *starts* at t
job_start = cp.Variable(M, integer=True)
job_end   = cp.Variable(M, integer=True)
earest_start = cp.Variable(integer=True)
latest_end   = cp.Variable(integer=True)

t_idx = np.arange(T)

# -----------------------
# 4) Constraints
# -----------------------
cons = []
# (A) Each job starts exactly once and within horizon
for j in range(M):
    cons.append(cp.sum(y[j, :]) == 1)
    for t in range(T - d[j] + 1, T):
        cons.append(y[j, t] == 0)
# (B) Node allocation
for k in range(K):
    for t in range(T):
        cons.append(cp.sum(x[:, k, t]) == 1)
# (C) Memory capacity per cluster/time
for i in range(N):
    for t in range(T):
        req = 0
        for j in range(M):
            for tau in range(max(0, t - d[j] + 1), t + 1):
                req += w[j] * c[j, i] * y[j, tau]
        cap = sum(s[k] * x[i, k, t] for k in range(K))
        cons.append(req <= cap)
# (D) Link start/end and makespan bounds
for j in range(M):
    cons.append(job_start[j] == cp.sum(cp.multiply(t_idx, y[j, :])))
    cons.append(job_end[j]   == job_start[j] + d[j] - 1)
    cons.append(earest_start <= job_start[j])
    cons.append(latest_end   >= job_end[j])
cons.append(earest_start >= 0)
cons.append(latest_end   <= T - 1)

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
        print(f" {j:>2} |    {int(job_start.value[j]):>2} | {int(job_end.value[j]):>2}")

# -----------------------
# 7) Plot & save charts
# -----------------------
if prob.status == cp.OPTIMAL:
    out_dir = "plots"
    os.makedirs(out_dir, exist_ok=True)

    cmap = plt.colormaps['tab10']
    colors = [cmap(i) for i in range(N)]

    # Combined Gantt chart colored by cluster with gridlines and integer xticks
    fig, ax = plt.subplots()
    for i in range(N):
        color = colors[i]
        jobs_i    = [j for j in range(M) if c[j, i] == 1]
        starts    = [job_start.value[j] for j in jobs_i]
        durations = [int(job_end.value[j] - job_start.value[j] + 1) for j in jobs_i]
        ax.barh(jobs_i, durations, left=starts, color=color, label=f'Cluster {i}')

    ax.set_yticks(list(range(M)))
    ax.set_ylabel('Job ID')
    ax.set_xlabel('Time slice')
    ax.set_title('All clusters schedule')
    ax.set_xticks(range(T+1))
    ax.grid(axis='x', linestyle='--', linewidth=0.5)
    ax.legend(title='Cluster')
    plt.tight_layout()
    combined_path = os.path.join(out_dir, 'all_clusters_schedule.png')
    plt.savefig(combined_path)
    plt.close(fig)
    print(f"Saved combined Gantt chart to {combined_path}")

    # Resource requirement vs available for each cluster in one graph
    fig, ax = plt.subplots()
    for i in range(N):
        color=colors[i]
        # compute requirement and availability over time
        req = [sum(w[j] for j in range(M) if c[j,i]==1 and job_start.value[j] <= t <= job_end.value[j]) for t in range(T)]
        avail = [sum(s[k] * x.value[i, k, t] for k in range(K)) for t in range(T)]
        ax.plot(range(T), req, marker='o', linestyle='-', color=color, label=f'Cluster {i} require')
        ax.plot(range(T), avail, marker='x', linestyle='--', color=color, label=f'Cluster {i} available')

    ax.set_xticks(range(T+1))
    ax.set_xlabel('Time slice')
    ax.set_ylabel('Memory')
    ax.set_title('Cluster Resource: Required vs Available')
    ax.grid(axis='x', linestyle='--', linewidth=0.5)
    ax.legend()
    plt.tight_layout()
    resource_path = os.path.join(out_dir, 'cluster_resource_comparison.png')
    plt.savefig(resource_path)
    plt.close(fig)
    print(f"Saved resource comparison plot to {resource_path}")

