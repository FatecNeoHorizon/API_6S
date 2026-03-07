package com.zeus.burndown.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.zeus.burndown.config.ScheduledBurndownChartGenerator;
import com.zeus.burndown.dto.response.GenerationResponse;
import com.zeus.burndown.integration.github.GitHubGraphQLClient;
import com.zeus.burndown.integration.github.GitHubProjectDataProvider;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/burndown")
@RequiredArgsConstructor
public class BurndownController {

    private final ScheduledBurndownChartGenerator scheduledBurndownChartGenerator;
    private final GitHubGraphQLClient gitHubGraphQLClient;
    private final GitHubProjectDataProvider gitHubProjectDataProvider;

    @PostMapping("/generate")
    public ResponseEntity<GenerationResponse> generateChart() {
        try {
            scheduledBurndownChartGenerator.genereteDailyChart();
            return ResponseEntity.ok(new GenerationResponse(
                true,
                "Gráfico gerado com sucesso!"
            ));
        } catch (Exception e) {
            return ResponseEntity.status(500).body(new GenerationResponse(
                false,
                "Erro ao gerar gráfico: " + e.getMessage()
            ));
        }
    }

    @GetMapping("/debug/raw")
    public ResponseEntity<String> debugRaw() {
        try {
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
            variables.put("org", "FatecNeoHorizon");
            variables.put("number", 3);
            variables.put("first", 50);
            variables.put("after", null);

            try {
                Object response = gitHubGraphQLClient.executeRaw(query, variables);
                ObjectMapper mapper = new ObjectMapper();
                String jsonResponse = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(response);

                return ResponseEntity.ok(jsonResponse);
            } catch (Exception e) {
                return ResponseEntity.status(500).body("Erro ao executar: " + e.getMessage());
            }
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Erro geral: " + e.getMessage());
        }
    }

    @GetMapping("/debug/auth")
    public ResponseEntity<String> debugAuth() {
        try {
            String query = """
                query {
                  viewer {
                    login
                    name
                  }
                }
            """;

            Object response = gitHubGraphQLClient.executeRaw(query, new HashMap<>());
            ObjectMapper mapper = new ObjectMapper();
            String jsonResponse = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(response);

            return ResponseEntity.ok(jsonResponse);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Erro: " + e.getMessage());
        }
    }

    @GetMapping("/debug/org")
    public ResponseEntity<String> debugOrg() {
        try {
            String query = """
                query($org: String!) {
                  organization(login: $org) {
                    name
                    projectsV2(first: 10) {
                      nodes {
                        number
                        title
                        id
                      }
                    }
                  }
                }
            """;

            Map<String, Object> variables = new HashMap<>();
            variables.put("org", "FatecNeoHorizon");

            Object response = gitHubGraphQLClient.executeRaw(query, variables);
            ObjectMapper mapper = new ObjectMapper();
            String jsonResponse = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(response);

            return ResponseEntity.ok(jsonResponse);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Erro: " + e.getMessage());
        }
    }

    @GetMapping("/debug/query")
    public ResponseEntity<String> debugQuery() {
        try {
            String query = """
                query($org: String!, $number: Int!, $first: Int!, $after: String) {
                  organization(login: $org) {
                    name
                    projectV2(number: $number) {
                      id
                      title
                      items(first: $first, after: $after) {
                        totalCount
                        pageInfo {
                          hasNextPage
                          endCursor
                        }
                        nodes {
                          content {
                            __typename
                            ... on Issue {
                              id
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
            variables.put("org", "FatecNeoHorizon");
            variables.put("number", 3);
            variables.put("first", 50);
            variables.put("after", null);

            Object response = gitHubGraphQLClient.executeRaw(query, variables);
            ObjectMapper mapper = new ObjectMapper();
            String jsonResponse = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(response);


            return ResponseEntity.ok(jsonResponse);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Erro: " + e.getMessage());
        }
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Serviço de Burndown está operacional");
    }
}
