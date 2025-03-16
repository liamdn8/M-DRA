package com.liamdn8;

import com.liamdn8.data.Cluster;
import com.liamdn8.data.Job;

import static com.liamdn8.Components.*;

public class Constraints {

    public static boolean resourceConstraint(Cluster cluster, Job job) {
        return cluster.getMemAvailable() >= job.getMem();
    }

    public static boolean jobTypeConstraint(Cluster cluster, Job job) {
        return job.getType().getRank() <= cluster.getType().getRank();
    }
}
