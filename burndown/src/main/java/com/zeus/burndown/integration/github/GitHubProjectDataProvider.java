package com.zeus.burndown.integration.github;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.zeus.burndown.dto.response.GraphQLResponse;
import com.zeus.burndown.integration.github.model.GitHubProjectQueryData;
import com.zeus.burndown.service.ProjectDataProvider;

@Service
public class GitHubProjectDataProvider implements ProjectDataProvider {

    private final GitHubGraphQLClient client;
    private final String org;
    private final int projectNumber;

    public GitHubProjectDataProvider(
                GitHubGraphQLClient client,
                @Value("${github.org}") String org,
                @Value("${github.project-number}") int projectNumber) {
        this.client = client;
        this.org = org;
        this.projectNumber = projectNumber;
    }

    @Override
    public GitHubProjectQueryData fetchProjectData() {
        String query = """
            query($org: String!, $number: Int!, $first: Int!, $after: String) {
              organization(login: $org) {
                projectV2(number: $number) {
                  items(first: $first, after: $after) {
                    pageInfo {
                      hasNextPage
                      endCursor
                    }
                    nodes {
                      content {
                        __typename
                        ... on Issue {
                          createdAt
                          closedAt
                          state
                          milestone {
                            createdAt
                            dueOn
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
        """;

        Map<String, Object> variables = new HashMap<>();
        variables.put("org", this.org);
        variables.put("number", this.projectNumber);
        variables.put("first", 50);
        variables.put("after", null);

        GraphQLResponse response = client.execute(query, variables);

        if (response == null) {
            throw new RuntimeException("GraphQL response is null");
        }


        if (response.getData() == null) {
            throw new RuntimeException("GraphQL returned no data");
        }

        return response.getData();
    }

}
