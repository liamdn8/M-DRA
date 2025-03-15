package com.liamdn8;

import com.liamdn8.data.Cluster;
import com.liamdn8.data.Job;
import com.liamdn8.data.Type;

import java.util.ArrayList;
import java.util.List;

public class Components {

    /*
     * List of jobs
     */
    public static List<Job> jobs = new ArrayList<>(List.of(
            new Job("11", Type.PERFORMANCE, 120, 120),
            new Job("12", Type.PERFORMANCE, 100, 120),
            new Job("13", Type.PERFORMANCE, 95, 120),
            new Job("14", Type.PERFORMANCE, 160, 120),
            new Job("15", Type.PERFORMANCE, 80, 120),
            new Job("21", Type.INTEGRATION, 60, 120),
            new Job("22", Type.INTEGRATION, 50, 120),
            new Job("23", Type.INTEGRATION, 60, 120),
            new Job("24", Type.INTEGRATION, 50, 120),
            new Job("25", Type.INTEGRATION, 55, 120),
            new Job("21", Type.FUNCTIONAL, 30, 120),
            new Job("22", Type.FUNCTIONAL, 20, 120),
            new Job("23", Type.FUNCTIONAL, 18, 120),
            new Job("24", Type.FUNCTIONAL, 24, 120),
            new Job("25", Type.FUNCTIONAL, 16, 120)
    ));

    public static List<Cluster> clusters = new ArrayList<>(List.of(
            new Cluster("1", Type.PERFORMANCE, 400),
            new Cluster("1", Type.INTEGRATION, 240),
            new Cluster("1", Type.FUNCTIONAL, 120)
    ));


}
