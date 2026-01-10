package com.example.evrouting.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Component
public class PythonSolverClient {

  private final WebClient web;

  public PythonSolverClient(@Value("${python.solverUrl}") String solverUrl) {
    this.web = WebClient.builder().baseUrl(solverUrl).build();
  }

  public Mono<String> solve(String jsonBody) {
    return web.post()
        .uri("/solve")
        .contentType(MediaType.APPLICATION_JSON)
        .bodyValue(jsonBody)
        .retrieve()
        .bodyToMono(String.class);
  }

  public Mono<String> health() {
    return web.get()
        .uri("/health")
        .retrieve()
        .bodyToMono(String.class);
  }
}