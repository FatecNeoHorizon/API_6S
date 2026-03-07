package com.zeus.burndown.integration.github.model;

import java.time.OffsetDateTime;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class IssueContent {

    @JsonProperty("__typename")
    private String typename;

    @JsonProperty("createdAt")
    private OffsetDateTime createdAt;

    @JsonProperty("closedAt")
    private OffsetDateTime closedAt;

    @JsonProperty("state")
    private String state;

    @JsonProperty("milestone")
    private Milestone milestone;

}
