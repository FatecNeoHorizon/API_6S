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
    private static final double DEFAULT_ITEM_HOURS = 1d;
 
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
            new SprintPeriod("Sprint 1", 16, 3, 5, 4),   // 16/03 - 05/04
            new SprintPeriod("Sprint 2", 13, 4, 3, 5),   // 13/04 - 03/05
            new SprintPeriod("Sprint 3", 11, 5, 31, 5)   // 11/05 - 31/05
    );
 
    public List<BurndownData> map(GitHubProjectQueryData data) {
 
        List<ProjectItemNode> allIssues = extractIssueNodes(data);
 
        List<BurndownData> result = new ArrayList<>();
 
        LocalDate today = LocalDate.now();
        SprintPeriod activeSprint = findActiveSprint(today);
 
        logger.debug("[DEBUG MAPPER] ====================================");
        logger.debug("[DEBUG MAPPER] Data atual: {}", today);
        logger.debug("[DEBUG MAPPER] Sprint ativa: {}", activeSprint.name);
        logger.debug("[DEBUG MAPPER] Período: {} até {}", activeSprint.start, activeSprint.end);
        logger.debug("[DEBUG MAPPER] Total de issues extraídas: {}", allIssues.size());
 
        if (!allIssues.isEmpty()) {
            logger.debug("[DEBUG MAPPER] Detalhes das issues:");
            allIssues.forEach(node -> {
                IssueContent issue = node.getContent();
                LocalDate created = toLocalDate(issue.getCreatedAt());
                LocalDate closed = issue.getClosedAt() != null ? toLocalDate(issue.getClosedAt()) : null;
                logger.debug("  - Criada: {} | Fechada: {} | Estado: {} | Estimativa(h): {}",
                        created,
                        closed,
                        issue.getState(),
                        resolveEstimateHours(node));
            });
        } else {
            logger.debug("[DEBUG MAPPER] NENHUMA ISSUE FOI EXTRAÍDA!");
        }
        logger.debug("[DEBUG MAPPER] ====================================");
 
        result.add(generateSprint(activeSprint.name,
                activeSprint.start,
                activeSprint.end,
                allIssues));
 
        return result;
    }
 
    private SprintPeriod findActiveSprint(LocalDate today) {
        for (SprintPeriod sprint : SPRINTS) {
            if (!today.isBefore(sprint.start) && !today.isAfter(sprint.end)) {
                return sprint;
            }
        }
 
        for (SprintPeriod sprint : SPRINTS) {
            if (today.isBefore(sprint.start)) {
                logger.warn("Nenhuma sprint ativa na data {}. Usando próxima sprint: {}", today, sprint.name);
                return sprint;
            }
        }
 
        SprintPeriod fallbackSprint = SPRINTS.stream()
                .filter(sprint -> "Sprint 3".equals(sprint.name))
                .findFirst()
                .orElse(SPRINTS.get(SPRINTS.size() - 1));
 
        logger.warn("Nenhuma sprint ativa ou próxima na data {}. Usando {} (padrão)", today, fallbackSprint.name);
        return fallbackSprint;
    }
 
    private List<ProjectItemNode> extractIssueNodes(GitHubProjectQueryData data) {
        return data.getOrganization()
                .getProject()
                .getItems()
                .getNodes()
                .stream()
                .filter(this::isIssueNode)
                .collect(Collectors.toList());
    }
 
    private BurndownData generateSprint(String sprintName,
                                    LocalDate start,
                                    LocalDate end,
                                    List<ProjectItemNode> allIssues) {

        LocalDate today = LocalDate.now();
        LocalDate plotEnd;
        if (today.isBefore(start)) {
            plotEnd = start;
        } else if (today.isAfter(end)) {
            plotEnd = end;
        } else {
            plotEnd = today;
        }

 
        List<ProjectItemNode> sprintIssues = allIssues.stream()
            .filter(node -> {
                LocalDate created = toLocalDate(node.getContent().getCreatedAt());
                return !created.isBefore(start) && !created.isAfter(end);
            })
            .collect(Collectors.toList());
 
        logger.debug("[DEBUG MAPPER] Issues do sprint '{}': {} de {} totais",
                sprintName, sprintIssues.size(), allIssues.size());
 
        double totalHours = sprintIssues.stream()
                                        .mapToDouble(this::resolveEstimateHours)
                                        .sum();
 
        logger.debug("[DEBUG MAPPER] Total de horas do sprint: {}", totalHours);
 
        long totalDays = start.datesUntil(end.plusDays(1)).count();
 
        List<LocalDate> dates = new ArrayList<>();
        List<Double> idealLine = new ArrayList<>();
        List<Double> realLine = new ArrayList<>();
     
        long dayIndex = 0;

        for (LocalDate date = start; !date.isAfter(plotEnd); date = date.plusDays(1)) {

            final LocalDate currentDate = date;
            dates.add(currentDate);
    
            double idealRemaining = totalDays <= 1
                    ? totalHours
                    : totalHours - (totalHours * dayIndex / (totalDays - 1));
    
            idealLine.add(Math.max(idealRemaining, 0));
    
            double closedHours = sprintIssues.stream()
                    .filter(node -> {
                        IssueContent issue = node.getContent();
                        if (issue.getClosedAt() == null) return false;
                        LocalDate closed = toLocalDate(issue.getClosedAt());
                        return !closed.isAfter(currentDate);
                    })
                    .mapToDouble(this::resolveEstimateHours)
                    .sum();
    
            realLine.add(Math.max(totalHours - closedHours, 0));
    
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
 
    private boolean isIssueNode(ProjectItemNode node) {
        IssueContent content = node.getContent();
        return content != null && "Issue".equals(content.getTypename());
    }
 
    private double resolveEstimateHours(ProjectItemNode node) {
        if (node.getEstimativa() == null) {
            return DEFAULT_ITEM_HOURS;
        }
 
        if (node.getEstimativa().getNumber() != null) {
            return normalizeHours(node.getEstimativa().getNumber());
        }
 
        if (node.getEstimativa().getText() != null) {
            return parseEstimateText(node.getEstimativa().getText());
        }
 
        return DEFAULT_ITEM_HOURS;
    }
 
    private double parseEstimateText(String value) {
        String normalized = value.trim().replace(',', '.').replaceAll("[^0-9.]", "");
        if (normalized.isBlank()) {
            return DEFAULT_ITEM_HOURS;
        }
 
        try {
            return normalizeHours(Double.parseDouble(normalized));
        } catch (NumberFormatException ex) {
            logger.warn("Não foi possível converter estimativa textual '{}' para número. Assumindo {}h.",
                    value,
                    DEFAULT_ITEM_HOURS);
            return DEFAULT_ITEM_HOURS;
        }
    }
 
    private double normalizeHours(double hours) {
        return hours <= 0d ? DEFAULT_ITEM_HOURS : hours;
    }
}
