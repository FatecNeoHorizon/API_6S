package com.zeus.burndown.integration.github;

import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import com.zeus.burndown.dto.request.GraphQLRequest;
import com.zeus.burndown.dto.response.GraphQLResponse;

@Component
public class GitHubGraphQLClient {

    private static final Logger logger = LoggerFactory.getLogger(GitHubGraphQLClient.class);
    private final WebClient webClient;

    public GitHubGraphQLClient(
            @Value("${burndown.github.api.url:${github.api.url}}") String apiUrl,
            @Value("${github.api.token}") String apiToken) {

        if (apiToken == null || apiToken.isBlank()) {
            logger.error("GitHub token não configurado. Chamadas à API vão falhar.");
        } else {
            logger.info("GitHub token configurado com sucesso.");
        }

        WebClient.Builder builder = WebClient.builder()
                .baseUrl(apiUrl)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE);

        if (apiToken != null && !apiToken.isBlank()) {
            builder.defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + apiToken);
        }

        this.webClient = builder.build();
    }

    public GraphQLResponse execute(String query, Map<String, Object> variables) {
        GraphQLRequest request = new GraphQLRequest();
        request.setQuery(query);
        request.setVariables(variables);

        return webClient.post()
                .bodyValue(request)
                .retrieve()
                .bodyToMono(GraphQLResponse.class)
                .doOnError(error -> logger.error("Erro na chamada GraphQL: {}", error.getMessage()))
                .block();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> executeRaw(String query, Map<String, Object> variables) {
        GraphQLRequest request = new GraphQLRequest();
        request.setQuery(query);
        request.setVariables(variables);

        return webClient.post()
                .bodyValue(request)
                .retrieve()
                .bodyToMono(Map.class)
                .doOnError(error -> logger.error("Erro na chamada GraphQL (raw): {}", error.getMessage()))
                .block();
    }
}
