package com.zeus.burndown;

import java.nio.file.Files;
import java.nio.file.Path;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.env.Environment;

import com.zeus.burndown.integration.github.model.GitHubProjectQueryData;
import com.zeus.burndown.model.BurndownData;
import com.zeus.burndown.service.BurndownChartGenerator;
import com.zeus.burndown.service.BurndownDataMapper;
import com.zeus.burndown.service.ProjectDataProvider;

@SpringBootApplication
public class BurndownApplication {

	private static final Logger logger = LoggerFactory.getLogger(BurndownApplication.class);
	private static final String DEFAULT_OUTPUT_PATH = "src/main/resources/static/burndown.png";

	public static void main(String[] args) {
		SpringApplication application = new SpringApplication(BurndownApplication.class);
		application.setWebApplicationType(WebApplicationType.NONE);
		ConfigurableApplicationContext context = application.run(args);

		int exitCode = runBurndown(context);
		int springExitCode = SpringApplication.exit(context, () -> exitCode);
		System.exit(springExitCode);
	}

	private static int runBurndown(ConfigurableApplicationContext context) {
		try {
			logger.info("Iniciando geracao do grafico burndown da sprint atual...");

			ProjectDataProvider projectDataProvider = context.getBean(ProjectDataProvider.class);
			BurndownDataMapper burndownDataMapper = context.getBean(BurndownDataMapper.class);
			BurndownChartGenerator burndownChartGenerator = context.getBean(BurndownChartGenerator.class);
			Environment environment = context.getEnvironment();

			String outputPath = environment.getProperty("burndown.output.path", DEFAULT_OUTPUT_PATH);
			String logoPath = environment.getProperty("burndown.logo.path", "");

			GitHubProjectQueryData projectData = projectDataProvider.fetchProjectData();
			BurndownData sprintData = burndownDataMapper.map(projectData)
					.stream()
					.findFirst()
					.orElseThrow(() -> new IllegalStateException("Nenhum dado de sprint foi gerado."));

			ensureOutputDirectoryExists(outputPath);

			String effectiveLogoPath = (logoPath == null || logoPath.isBlank()) ? null : logoPath;
			burndownChartGenerator.generateBurndownChart(sprintData, outputPath, effectiveLogoPath);

			logger.info("Grafico gerado com sucesso em: {}", outputPath);
			return 0;
		} catch (Exception e) {
			logger.error("Falha ao gerar grafico burndown.", e);
			return 1;
		}
	}

	private static void ensureOutputDirectoryExists(String filePath) throws Exception {
		Path outputFile = Path.of(filePath);
		Path parent = outputFile.getParent();

		if (parent != null) {
			Files.createDirectories(parent);
		}
	}

}
