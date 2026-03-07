package com.zeus.burndown.service;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import com.zeus.burndown.integration.github.model.GitHubProjectQueryData;
import com.zeus.burndown.integration.github.model.IssueContent;
import com.zeus.burndown.integration.github.model.ProjectItemNode;
import com.zeus.burndown.model.BurndownData;

@Component
public class BurndownDataMapper {

    private static final Logger logger = LoggerFactory.getLogger(BurndownDataMapper.class);
    private static final ZoneId ZONE = ZoneId.systemDefault();
    
    // Definição das sprints
    private static class SprintPeriod {
        String name;
        LocalDate start;
        LocalDate end;
        
        SprintPeriod(String name, int startDay, int startMonth, int endDay, int endMonth) {
            this.name = name;
            this.start = LocalDate.of(2026, startMonth, startDay);
            this.end = LocalDate.of(2026, endMonth, endDay);
        }
    }
    
    private static final List<SprintPeriod> SPRINTS = List.of(
        new SprintPeriod("Sprint 0", 1, 2, 10, 3),    // 01/02 - 10/03 (Teste)
        new SprintPeriod("Sprint 1", 16, 3, 5, 4),    // 16/03 - 05/04
        new SprintPeriod("Sprint 2", 13, 4, 3, 5),    // 13/04 - 03/05
        new SprintPeriod("Sprint 3", 11, 5, 31, 5)    // 11/05 - 31/05
    );

    public List<BurndownData> map(GitHubProjectQueryData data) {

        List<IssueContent> allIssues = extractIssues(data);

        List<BurndownData> result = new ArrayList<>();

        LocalDate today = LocalDate.now();
        SprintPeriod activeSprint = findActiveSprint(today);
        
        System.out.println("\n[DEBUG MAPPER] ====================================");
        System.out.println("[DEBUG MAPPER] Data atual: " + today);
        System.out.println("[DEBUG MAPPER] Sprint ativa: " + activeSprint.name);
        System.out.println("[DEBUG MAPPER] Período: " + activeSprint.start + " até " + activeSprint.end);
        System.out.println("[DEBUG MAPPER] Total de issues extraídas: " + allIssues.size());
        
        if (!allIssues.isEmpty()) {
            System.out.println("[DEBUG MAPPER] Detalhes das issues:");
            allIssues.forEach(issue -> {
                LocalDate created = toLocalDate(issue.getCreatedAt());
                LocalDate closed = issue.getClosedAt() != null ? toLocalDate(issue.getClosedAt()) : null;
                System.out.println("  - Criada: " + created + " | Fechada: " + closed + " | Estado: " + issue.getState());
            });
        } else {
            System.out.println("[DEBUG MAPPER] ❌ NENHUMA ISSUE FOI EXTRAÍDA!");
        }
        System.out.println("[DEBUG MAPPER] ====================================\n");

        result.add(generateSprint(activeSprint.name,
                activeSprint.start,
                activeSprint.end,
                allIssues));

        return result;
    }

    /**
     * Encontra qual sprint está ativa baseado na data atual
     */
    private SprintPeriod findActiveSprint(LocalDate today) {
        for (SprintPeriod sprint : SPRINTS) {
            if (!today.isBefore(sprint.start) && !today.isAfter(sprint.end)) {
                return sprint;
            }
        }
        
        // Se nenhuma sprint estiver ativa, retorna a última
        logger.warn("Nenhuma sprint ativa na data {}. Usando Sprint 3 (padrão)", today);
        return SPRINTS.get(SPRINTS.size() - 1);
    }

    private List<IssueContent> extractIssues(GitHubProjectQueryData data) {


        List<IssueContent> issues = data.getOrganization()
                .getProject()
                .getItems()
                .getNodes()
                .stream()
                .map(ProjectItemNode::getContent)
                .filter(content -> content != null)
                .filter(content -> "Issue".equals(content.getTypename()))
                .collect(Collectors.toList());
        
        return issues;
    }

    private BurndownData generateSprint(String sprintName,
                                        LocalDate start,
                                        LocalDate end,
                                        List<IssueContent> allIssues) {

        LocalDate today = LocalDate.now();
        LocalDate effectiveEnd = end.isAfter(today) ? today : end;

        List<IssueContent> sprintIssues = allIssues.stream()
                .filter(issue -> {
                    LocalDate created = toLocalDate(issue.getCreatedAt());
                    return !created.isBefore(start) && !created.isAfter(effectiveEnd);
                })
                .collect(Collectors.toList());

        int totalIssues = sprintIssues.size();
        long totalDays = start.datesUntil(end.plusDays(1)).count();

        List<LocalDate> dates = new ArrayList<>();
        List<Double> idealLine = new ArrayList<>();
        List<Double> realLine = new ArrayList<>();

        long dayIndex = 0;

        for (LocalDate date = start; !date.isAfter(effectiveEnd); date = date.plusDays(1)) {

            final LocalDate currentDate = date;
            dates.add(currentDate);

            double idealRemaining = totalIssues -
                    ((double) totalIssues * dayIndex / (totalDays - 1));

            idealLine.add(Math.max(idealRemaining, 0));

            long closedCount = sprintIssues.stream()
                    .filter(issue -> {
                        if (issue.getClosedAt() == null) return false;
                        LocalDate closed = toLocalDate(issue.getClosedAt());
                        return !closed.isAfter(currentDate);
                    })
                    .count();

            double realRemaining = totalIssues - closedCount;

            realLine.add(Math.max(realRemaining, 0));

            dayIndex++;
        }

        BurndownData burndown = new BurndownData();
        burndown.setSprintName(sprintName);
        burndown.setStartDate(start);
        burndown.setEndDate(end);
        burndown.setDates(dates);
        burndown.setIdealLine(idealLine);
        burndown.setRealLine(realLine);

        return burndown;
    }

    private LocalDate toLocalDate(OffsetDateTime dateTime) {
        return dateTime.atZoneSameInstant(ZONE).toLocalDate();
    }
}
