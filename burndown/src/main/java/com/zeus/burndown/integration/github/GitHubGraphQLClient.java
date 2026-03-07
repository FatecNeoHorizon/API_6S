package com.zeus.burndown.integration.github;

import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

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

    private static final Logger logger = Logger.getLogger(GitHubGraphQLClient.class.getName());
    private static final org.slf4j.Logger logger4j = LoggerFactory.getLogger(GitHubGraphQLClient.class);
    private final WebClient webClient;

    /**
     * Construtor que inicializa o cliente GraphQL do GitHub.
     * 
     * Cria uma instância do WebClient com as configurações necessárias para fazer 
     * requisições à API GraphQL do GitHub. Se o token não estiver configurado, 
     * um aviso será registrado, mas a aplicação continuará funcionando (útil para desenvolvimento).
     * 
     * @param apiUrl URL base da API do GitHub (obtida da propriedade github.api.url)
     * @param apiToken Token de autenticação do GitHub (obtido da propriedade github.api.token)
     */

    public GitHubGraphQLClient(
                                @Value("${github.api.url}") String apiUrl,
                                @Value("${github.api.token}") String apiToken) {
        if (apiToken == null || apiToken.isBlank()) {
            logger4j.error("GitHub token not configured. API calls will fail without a valid token.");
            logger.log(Level.SEVERE, "GitHub token not configured!");
        } else {
            logger4j.info("GitHub token configured successfully");
        }
        
        WebClient.Builder builder = WebClient.builder()
                                  .baseUrl(apiUrl)
                                  .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE);
        
        // Adiciona o header de autenticação apenas se o token estiver configurado
        if (apiToken != null && !apiToken.isBlank()) {
            builder.defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + apiToken);
        }
        
        this.webClient = builder.build();
    }

    /**
     * Executa uma query GraphQL contra a API do GitHub.
     * 
     * Constrói uma requisição GraphQL com a query e variáveis fornecidas,
     * envia para a API do GitHub e retorna a resposta serializada como objeto.
     * 
     * @param query A query GraphQL a ser executada
     * @param variables Mapa de variáveis para substituir na query (pode ser null)
     * @return GraphQLResponse contendo os dados ou erros retornados pela API
     * @throws Exception se houver erro na comunicação com a API
     */

    public GraphQLResponse execute(String query, Map<String, Object> variables) {
        
        GraphQLRequest request = new GraphQLRequest();
        request.setQuery(query);
        request.setVariables(variables);

        return webClient.post()
                        .bodyValue(request)
                        .retrieve()
                        .bodyToMono(GraphQLResponse.class)
                        .doOnError(error -> logger.log(Level.SEVERE, "Error: {0}", error.getMessage()))
                        .block();
    }

    /**
     * Executa uma query GraphQL e retorna a resposta bruta como Map.
     * Útil para debug e análise da resposta completa.
     */
    public Map<String, Object> executeRaw(String query, Map<String, Object> variables) {
        
        GraphQLRequest request = new GraphQLRequest();
        request.setQuery(query);
        request.setVariables(variables);

        return webClient.post()
                        .bodyValue(request)
                        .retrieve()
                        .bodyToMono(Map.class)
                        .doOnError(error -> logger.log(Level.SEVERE, "Error: {0}", error.getMessage()))
                        .block();
    }

}
