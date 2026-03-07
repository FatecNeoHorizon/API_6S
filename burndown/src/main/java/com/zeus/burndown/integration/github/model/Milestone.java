package com.zeus.burndown.integration.github.model;

import java.time.LocalDate;
import java.time.OffsetDateTime;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class Milestone {
    
    @JsonProperty("createdAt")
    private OffsetDateTime createdAt;

    @JsonProperty("dueOn")
    private LocalDate dueOn;

}
