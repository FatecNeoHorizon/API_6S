package com.zeus.burndown.integration.github;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import com.zeus.burndown.dto.response.GraphQLResponse;
import com.zeus.burndown.integration.github.model.GitHubProjectQueryData;
import com.zeus.burndown.integration.github.model.ProjectItemNode;
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

    private static final String QUERY = """
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
                  estimativa: fieldValueByName(name: "Estimativa (h)") {
                    __typename
                    ... on ProjectV2ItemFieldNumberValue {
                      number
                    }
                    ... on ProjectV2ItemFieldTextValue {
                      text
                    }
                  }
                }
              }
            }
          }
        }
    """;

    @Override
    public GitHubProjectQueryData fetchProjectData() {
        String after = null;
        boolean hasNextPage = true;

        List<ProjectItemNode> allNodes = new ArrayList<>();
        GitHubProjectQueryData finalData = null;

        do {
            Map<String, Object> variables = new HashMap<>();
            variables.put("org", this.org);
            variables.put("number", this.projectNumber);
            variables.put("first", 50);
            variables.put("after", after);

            GraphQLResponse response = client.execute(QUERY, variables);

            if (response == null) {
                throw new RuntimeException("GraphQL response is null");
            }
            if (response.getData() == null) {
                throw new RuntimeException("GraphQL returned no data");
            }

            GitHubProjectQueryData pageData = response.getData();

            if (finalData == null) {
                finalData = pageData;
            }

            var items = pageData
                    .getOrganization()
                    .getProject()
                    .getItems();

            allNodes.addAll(items.getNodes());

            hasNextPage = items.getPageInfo().isHasNextPage();
            after = items.getPageInfo().getEndCursor();

        } while (hasNextPage);

        finalData
            .getOrganization()
            .getProject()
            .getItems()
            .setNodes(allNodes);

        return finalData;
    }
}
