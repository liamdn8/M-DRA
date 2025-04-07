import cvxpy as cp
import numpy as np

time_slice = 100
T = 100

class Cluster:
  def __init__(self, id):
    self.id = id

class Node:
  def __init__(self, id, cpu, mem):
    self.id = id
    self.cpu_cap = cpu
    self.mem_cap = mem

class Job:
  def __init__(self, id, cluster_id, cpu, mem, start, end):
    self.id = id
    self.cluster_id = cluster_id
    self.cpu_req = cpu
    self.mem_req = mem
    self.schedule_slice = self.get_schedule(start, end)

  def get_schedule(self, start, end):
    schedule_slice = []
    for t in range(time_slice):
      if(start >= t and end <= t):
        schedule_slice.append(1)
      else: pass
    return schedule_slice


# -----------------------------
# Data Setup
# -----------------------------
# Cluster Setup
# Cluster i = 0..N-1
N = 5

print("-----------------------------")
print("Number of time slices: ", time_slice)
print("-----------------------------")
print("Number of clusters: ", N)
print("-----------------------------\n")

# -----------------------------
# Node k = 0..K-1
# Node CPU capacity R_k
# Node Mem capacity S_k
nodes_obj = [
    Node(1, 10, 24),
    Node(2, 10, 24),
    Node(3, 10, 24),
    Node(4, 10, 24),
    Node(5, 10, 24),
    Node(6, 10, 24),
    Node(7, 10, 24),
    Node(8, 10, 24),
    Node(9, 10, 24),
    Node(10, 10, 24)
]

K = len(nodes_obj)

node_cpu_caps=[]
node_mem_caps=[]

for node in nodes_obj:
  node_cpu_caps.append(node.cpu_cap)
  node_mem_caps.append(node.mem_cap)

print("-----------------------------")
print("Number of nodes: ", len(nodes_obj))
print("-----------------------------\n")
print("Node cpu capacity:")
print(node_cpu_caps)
print("Node mem capacity:")
print(node_mem_caps)

# -----------------------------
# Job j = 0..M-1
# Job CPU required C_j
# Job Mem required E_j
jobs_obj = [
    Job(1, 1, 4, 12, 3, 6),
    Job(2, 1, 4, 12, 5, 6),
    Job(3, 1, 4, 12, 7, 10),
    Job(4, 2, 4, 12, 4, 5),
    Job(5, 2, 4, 12, 9, 15),
    Job(6, 3, 4, 12, 13, 20),
    Job(7, 3, 4, 12, 10, 12),
    Job(8, 3, 4, 12, 15, 18),
    Job(9, 4, 4, 12, 8, 11),
    Job(10, 4, 4, 12, 8, 15),
    Job(11, 4, 4, 12, 7, 14),
    Job(12, 1, 4, 12, 5, 10),
    Job(13, 1, 4, 12, 12, 16),
    Job(14, 2, 4, 12, 9, 11),
    Job(15, 2, 4, 12, 2, 6),
]

M = len(jobs_obj)

job_cpu_reqs = []
job_mem_reqs = []
job_scheduled = []

for job in jobs_obj:
  job_cpu_reqs.append(job.cpu_req)
  job_mem_reqs.append(job.mem_req)
  job_scheduled.append(job.get_schedule)

print("-----------------------------")
print("Number of jobs: ", len(jobs_obj))
print("-----------------------------\n")
print("Job cpu required:")
print(job_cpu_reqs)
print("Job mem required:")
print(job_mem_reqs)

# -----------------------------
# Job j scheduled to run on cluster i
print("-----------------------------\n")
print("Job scheduled map")
job_cluster_schedule_map = []
for cluster_id in range(N-1):
  job_cluster_schedule_map.append([])
  job_cluster_schedule_map[cluster_id] = []
  for job in jobs_obj:
    if job.cluster_id == cluster_id:
      job_cluster_schedule_map[cluster_id].append(1)
    else:
      job_cluster_schedule_map[cluster_id].append(0)
  print(job_cluster_schedule_map[cluster_id])
