package com.zeus.burndown.config;

import java.io.File;
import java.util.List;

import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.stereotype.Component;

import com.zeus.burndown.integration.github.model.GitHubProjectQueryData;
import com.zeus.burndown.model.BurndownData;
import com.zeus.burndown.service.BurndownChartGenerator;
import com.zeus.burndown.service.BurndownDataMapper;
import com.zeus.burndown.service.ProjectDataProvider;

import lombok.RequiredArgsConstructor;

@Component
@EnableScheduling
@RequiredArgsConstructor
public class ScheduledBurndownChartGenerator {

    private final ProjectDataProvider projectDataProvider;
    private final BurndownDataMapper burndownDataMapper;
    private final BurndownChartGenerator burndownChartGenerator;

    public void genereteDailyChart(){

        try {
            GitHubProjectQueryData data = projectDataProvider.fetchProjectData();
            List<BurndownData> sprints = burndownDataMapper.map(data);
           
            for (BurndownData sprint : sprints) {
                
                String outputPath = getOutputPath() + "burndown.png";
                File file = new File(outputPath);

                if (!file.getParentFile().exists()) {
                    file.getParentFile().mkdirs();
                }

                try {
                    burndownChartGenerator.generateBurndownChart(sprint, outputPath, null);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
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
