FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml /app/pom.xml
COPY src /app/src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/evrouting-0.1.0.jar /app/app.jar
EXPOSE 8080
ENV PY_SOLVER_URL=http://localhost:8000
CMD ["java", "-jar", "/app/app.jar"]