package com.liamdn8;

import com.liamdn8.data.*;

import static com.liamdn8.Components.*;
import static com.liamdn8.Constraints.*;

public class Scheduler {
    public static void main(String[] argv) {

        for (Cluster cluster : clusters) {
            for (Job job : jobs) {
                if (jobTypeConstraint(cluster, job) && resourceConstraint(cluster, job)) {
                    allocate(cluster, job);
                }

                if (cluster.getMemAvailable() <= 0) {
                    break;
                }
            }
        }



    }

    public static void allocate(Cluster cluster, Job job) {
        job.setAllocated(true);
        cluster.setMemAvailable(cluster.getMemAvailable() - job.getMem());
    }
}
