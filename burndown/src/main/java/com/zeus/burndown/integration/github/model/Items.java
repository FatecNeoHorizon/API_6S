package com.zeus.burndown.integration.github.model;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class Items {

    @JsonProperty("nodes")
    private List<ProjectItemNode> nodes;

    @JsonProperty("pageInfo")
    private PageInfo pageInfo;

}
