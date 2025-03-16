package com.liamdn8.data;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter @Setter
@AllArgsConstructor
@NoArgsConstructor
public class Job {
    String id;
    Type type;
    int mem;
    int duration;

    boolean isAllocated;
    boolean isFailed;

    int startTime;
    int endTime;
    Cluster cluster;

    public Job(String id, Type type, int mem, int duration) {
        this.id = id;
        this.type = type;
        this.mem = mem;
        this.duration = duration;
    }

    public void allocate(Cluster cluster, int triggeredTime) {
        this.setAllocated(true);
        this.cluster = cluster;

        this.startTime = triggeredTime;
        this.endTime = triggeredTime + this.duration;
    }
}
