package com.zeus.burndown.dto.response;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class GenerationResponse {
    
    private boolean success;
    private String message;
}
