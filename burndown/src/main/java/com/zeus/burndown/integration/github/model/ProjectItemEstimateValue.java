package com.zeus.burndown.integration.github.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class ProjectItemEstimateValue {

    @JsonProperty("__typename")
    private String typename;

    @JsonProperty("number")
    private Double number;

    @JsonProperty("text")
    private String text;
}