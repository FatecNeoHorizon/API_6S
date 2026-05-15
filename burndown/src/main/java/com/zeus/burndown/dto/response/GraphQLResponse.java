package com.zeus.burndown.dto.response;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.zeus.burndown.integration.github.model.GitHubProjectQueryData;

import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class GraphQLResponse {

    private GitHubProjectQueryData data;
    private List<Object> errors;
}
