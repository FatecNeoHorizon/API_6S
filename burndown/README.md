# Burndown Automatic Generator <a ></a>

[Back to main README](../README.md#date-sprint-backlog)

Java/Spring Boot project to automatically generate a burndown chart based on real GitHub Projects Issue data (GraphQL API).

## Overview

Execution flow:
1. `ProjectDataProvider` fetches data from the GitHub Project via GraphQL.
2. `BurndownDataMapper` transforms Issues into a time series for the active sprint.
3. `BurndownChartGenerator` generates the chart PNG.
4. `BurndownApplication` orchestrates everything and exits with an `exit code`.

Default chart output:
- `src/main/resources/static/burndown.png`

## Authorship and Project Leadership

This project was entirely conceived, architected, implemented and operationalized by **Cesar Pelogia**.

End-to-end responsibilities:
- idea conception and problem definition
- architecture design and solution modeling
- application development and GitHub GraphQL API integration
- GitHub Actions execution automation
- technical validation, troubleshooting and delivery stabilization

Professional profiles:
- GitHub: `https://github.com/cesarpelogia`
- LinkedIn: `http://www.linkedin.com/in/cesar-augusto-anselmo-pelogia-truyts-94a08a268/`

## Stack

- Java 21
- Spring Boot 4
- Maven Wrapper (`mvnw` / `mvnw.cmd`)
- JFreeChart
- GitHub GraphQL API
- GitHub Actions

## Main Structure

- `src/main/java/com/zeus/burndown/BurndownApplication.java`: entry point and orchestration
- `src/main/java/com/zeus/burndown/integration/github/`: GitHub API client and provider
- `src/main/java/com/zeus/burndown/service/`: mapping rules and chart generation
- `src/main/resources/application.properties`: environment configuration
- `.github/workflows/burndowngenerate.yml`: CI automation to generate and publish the chart

## Configuration

### Relevant variables/properties

In `application.properties`:

```properties
github.api.url=https://api.github.com/graphql
github.api.token=${GITHUB_TOKEN:}
github.org={Organization_Name}
github.project-number={Project_Number}

burndown.output.path=src/main/resources/static/burndown.png
burndown.logo.path=
```

### Token

The application reads the token from the `GITHUB_TOKEN` environment variable.

In GitHub Actions, the `ISSUE_TOKEN_API` secret is mapped to `GITHUB_TOKEN` in the workflow.

## Local Execution

### Windows (cmd)

```bat
cd burndown
set GITHUB_TOKEN=your_token_here
mvnw.cmd spring-boot:run
```

### Windows (PowerShell)

```powershell
cd burndown
$env:GITHUB_TOKEN="your_token_here"
./mvnw.cmd spring-boot:run
```

### Running via JAR (same pattern as CI)

```bat
cd burndown
mvnw.cmd clean package -DskipTests
set GITHUB_TOKEN=your_token_here
java -jar target/burndown-0.0.1-SNAPSHOT.jar
```

## Tests

```bat
cd burndown
mvnw.cmd test
```

## GitHub Actions (Automation)

Workflow:
- `/.github/workflows/burndowngenerate.yml`

Behavior:
- runs daily via `cron` and also manually (`workflow_dispatch`)
- compiles the `burndown` module
- executes the JAR to generate the PNG
- commits/pushes `src/main/resources/static/burndown.png` when there are changes

## Quick Troubleshooting

- GitHub authentication error:
  - verify that `GITHUB_TOKEN` was set with the actual PAT value.
- No data in the chart:
  - confirm `github.org` and `github.project-number`.
- Workflow does not commit:
  - the chart may not have changed that day.

## Expected Result

On successful execution:
- logs report the start/end of the generation
- the file `src/main/resources/static/burndown.png` is updated
- in CI, the chart can be automatically versioned via commit