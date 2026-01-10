package com.example.evrouting.controller;

import com.example.evrouting.client.PythonSolverClient;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

@RestController
public class SolveController {

  private final PythonSolverClient client;

  public SolveController(PythonSolverClient client) {
    this.client = client;
  }

  @GetMapping("/health")
  public Mono<String> health() {
    return client.health();
  }

  @PostMapping(
      value = "/solve",
      consumes = MediaType.APPLICATION_JSON_VALUE,
      produces = MediaType.APPLICATION_JSON_VALUE
  )
  public Mono<String> solve(@RequestBody String body) {
    return client.solve(body);
  }
}