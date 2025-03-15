package com.liamdn8.data;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
public class Cluster {
    String id;
    Type type;
    int memCapacity;
    int memAvailable;

    public Cluster(String id, Type type, int memCapacity) {
        this.id = id;
        this.type = type;
        this.memCapacity = memCapacity;
    }
}
