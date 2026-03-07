package com.zeus.burndown.config;

import java.io.File;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import com.zeus.burndown.integration.github.model.GitHubProjectQueryData;
import com.zeus.burndown.model.BurndownData;
import com.zeus.burndown.service.BurndownChartGenerator;
import com.zeus.burndown.service.BurndownDataMapper;
import com.zeus.burndown.service.ProjectDataProvider;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class ScheduledBurndownChartGenerator {

    private static final Logger logger = LoggerFactory.getLogger(ScheduledBurndownChartGenerator.class);

    private final ProjectDataProvider projectDataProvider;
    private final BurndownDataMapper burndownDataMapper;
    private final BurndownChartGenerator burndownChartGenerator;

    @PostConstruct
    public void genereteDailyChart(){
        logger.info("🔄 [BURNDOWN] Iniciando geração de gráfico de burndown...");

        try {
            logger.info("📊 [BURNDOWN] Buscando dados do GitHub...");
            GitHubProjectQueryData data = projectDataProvider.fetchProjectData();
            List<BurndownData> sprints = burndownDataMapper.map(data);
           
            logger.info("✅ [BURNDOWN] {} sprint(s) encontrada(s)", sprints.size());

            for (BurndownData sprint : sprints) {
                logger.info("📈 [BURNDOWN] Gerando gráfico para sprint: {}", sprint.getSprintName());
                
                String outputPath = getOutputPath() + "burndown.png";
                File file = new File(outputPath);

                if (!file.getParentFile().exists()) {
                    logger.info("📂 [BURNDOWN] Criando diretório: {}", file.getParentFile().getAbsolutePath());
                    file.getParentFile().mkdirs();
                }

                try {
                    burndownChartGenerator.generateBurndownChart(sprint, outputPath, null);
                    logger.info("✅ [BURNDOWN] Gráfico gerado com sucesso em: {}", outputPath);
                } catch (Exception e) {
                    logger.error("❌ [BURNDOWN] Erro ao gerar gráfico: ", e);
                }
            }

            logger.info("✅ [BURNDOWN] Geração concluída!");

        } catch (Exception e) {
            logger.error("❌ [BURNDOWN] Erro crítico na geração: ", e);
        }

    }

    private String getOutputPath() {
        String githubWorkspace = System.getenv("GITHUB_WORKSPACE");
        
        if (githubWorkspace != null && !githubWorkspace.isEmpty()) {
            return githubWorkspace + "/src/main/resources/static/";
        }
        
        return "src/main/resources/static/";
    }

}
