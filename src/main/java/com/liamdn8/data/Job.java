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

    public Job(String id, Type type, int mem, int duration) {
        this.id = id;
        this.type = type;
        this.mem = mem;
        this.duration = duration;
    }
}
