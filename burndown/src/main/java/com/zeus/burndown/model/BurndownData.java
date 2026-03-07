package com.zeus.burndown.model;

import java.time.LocalDate;
import java.util.List;

import lombok.Data;

@Data
public class BurndownData {

    String sprintName;
    LocalDate startDate;
    LocalDate endDate;
    List<LocalDate> dates;
    List<Double> idealLine;
    List<Double> realLine;

}
