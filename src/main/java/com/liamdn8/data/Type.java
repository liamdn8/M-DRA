package com.liamdn8.data;

import lombok.Getter;

@Getter
public enum Type {
    PERFORMANCE(1),
    INTEGRATION(2),
    FUNCTIONAL(3);

    private final int rank;

    Type(int rank) {
        this.rank = rank;
    }
}
