package com.liamdn8;

import com.liamdn8.data.*;

import java.util.LinkedList;

import static com.liamdn8.Components.*;
import static com.liamdn8.Constraints.*;

public class Scheduler {
    public static void main(String[] argv) {


        int timeIndex = 0;
        while (timeIndex < timeRange) {
            System.out.printf("\nTimestamp: %s", timeIndex);

            doSchedule(timeIndex);
            updateSystemStatus(timeIndex);

            timeIndex = timeIndex + 120;
        }
    }

    public static void allocate(Cluster cluster, Job job, int allocatedTime) {
        job.allocate(cluster, allocatedTime);
        cluster.startJob(job);
    }

    public static void doSchedule(int timeIndex) {
        // job allocate
        for (Cluster cluster : clusters) {
            System.out.printf("\nSchedule on cluster %s - %s", cluster.getId(), cluster.getType());

            while (!jobQueue.isEmpty()) {
                Job job = jobQueue.poll();
                System.out.printf("\nChecking job %s on cluster %s", job.getId(), cluster.getId());

                if (jobTypeConstraint(cluster, job) && resourceConstraint(cluster, job)) {
                    allocate(cluster, job, timeIndex);
                    processJobQueue.add(job);
                    System.out.printf("\nAllocated job %s on cluster %s", job.getId(), cluster.getId());
                } else {
                    skippedJobQueue.add(job);
                }
            }
            System.out.printf("\nCluster %s mem available after schedule: %s", cluster.getId(), cluster.getMemAvailable());

            jobQueue = skippedJobQueue;
            skippedJobQueue = new LinkedList<>();
        }
    }

    public static void updateSystemStatus(int timeIndex) {
        for (Job job : processJobQueue) {
            if (job.isAllocated()) {
                if (timeIndex < job.getEndTime()) {
                    System.out.printf("\nJob %s end on cluster %s", job.getId(), job.getCluster().getId());
                    job.getCluster().endJob(job);
                }
            }
        }
    }
}
