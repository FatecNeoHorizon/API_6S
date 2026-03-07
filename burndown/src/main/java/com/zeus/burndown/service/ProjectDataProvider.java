package com.zeus.burndown.service;

import com.zeus.burndown.integration.github.model.GitHubProjectQueryData;

public interface ProjectDataProvider {

    GitHubProjectQueryData fetchProjectData();
}
