package com.liamdn8.data;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.HashSet;
import java.util.Set;

@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
public class Cluster {
    String id;
    Type type;
    int memCapacity;
    int memAvailable;

    Set<Job> runningJobs = new HashSet<>();

    public Cluster(String id, Type type, int memCapacity) {
        this.id = id;
        this.type = type;
        this.memCapacity = memCapacity;
        this.memAvailable = memCapacity;
    }

    public void startJob(Job job) {
        this.memAvailable = this.memAvailable - job.getMem();
        this.runningJobs.add(job);
    }

    public void endJob(Job job) {
        this.memAvailable = this.memAvailable + job.getMem();
        this.runningJobs.remove(job);
        job.setAllocated(false);
    }
}
