#!/usr/bin/env python3
"""Fullstack Development - Java: 65 MCQ questions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from seed_data.common import make_mcq, insert_domain_questions

DOMAIN = "Fullstack Development - Java"

questions = [
    # ── EASY (20) ──────────────────────────────────────────────
    make_mcq(
        "Which annotation marks the main class of a Spring Boot application?",
        ["@SpringBootApplication", "@Component", "@RestController", "@Configuration"],
        "A", "Easy"),
    make_mcq(
        "What does the @RestController annotation combine?",
        ["@Controller and @ResponseBody", "@Service and @Component", "@RequestMapping and @PathVariable", "@Configuration and @Bean"],
        "A", "Easy"),
    make_mcq(
        "Which HTTP method is typically used to create a new resource in a REST API?",
        ["GET", "POST", "PUT", "DELETE"],
        "B", "Easy"),
    make_mcq(
        "In Spring Boot, which file is used for application configuration by default?",
        ["config.xml", "application.properties", "settings.json", "web.xml"],
        "B", "Easy"),
    make_mcq(
        "What does JPA stand for?",
        ["Java Persistence API", "Java Programming Architecture", "Java Page Application", "Java Platform Abstraction"],
        "A", "Easy"),
    make_mcq(
        "Which build tool uses a pom.xml file?",
        ["Gradle", "Ant", "Maven", "SBT"],
        "C", "Easy"),
    make_mcq(
        "What is the default port for a Spring Boot application?",
        ["3000", "8080", "5000", "9090"],
        "B", "Easy"),
    make_mcq(
        "Which annotation maps an HTTP GET request to a handler method in Spring MVC?",
        ["@PostMapping", "@GetMapping", "@PutMapping", "@RequestBody"],
        "B", "Easy"),
    make_mcq(
        "What does CORS stand for?",
        ["Cross-Origin Resource Sharing", "Common Object Resource Standard", "Cross-Origin Request Service", "Client Object Response Specification"],
        "A", "Easy"),
    make_mcq(
        "Which annotation is used to inject a dependency automatically in Spring?",
        ["@Inject", "@Autowired", "@Resource", "@Bean"],
        "B", "Easy"),
    make_mcq(
        "In a Spring Boot REST API, which annotation is used to bind a request body to a Java object?",
        ["@RequestParam", "@PathVariable", "@RequestBody", "@ModelAttribute"],
        "C", "Easy"),
    make_mcq(
        "Which Java testing framework is most commonly used with Spring Boot?",
        ["TestNG", "JUnit", "Spock", "Cucumber"],
        "B", "Easy"),
    make_mcq(
        "What does DTO stand for in enterprise Java applications?",
        ["Data Transfer Object", "Database Transaction Operation", "Dynamic Type Object", "Data Type Organizer"],
        "A", "Easy"),
    make_mcq(
        "Which Spring annotation marks a class as a service layer component?",
        ["@Repository", "@Controller", "@Service", "@Component"],
        "C", "Easy"),
    make_mcq(
        "What is the purpose of the @Entity annotation in JPA?",
        ["Marks a class as a REST controller", "Maps a Java class to a database table", "Defines a Spring bean", "Marks a method as transactional"],
        "B", "Easy"),
    make_mcq(
        "Which packaging format allows a Spring Boot app to run as a standalone executable?",
        ["WAR", "EAR", "JAR", "RAR"],
        "C", "Easy"),
    make_mcq(
        "What does the @PathVariable annotation extract in a Spring controller?",
        ["Query parameters", "Request body fields", "URI template variables", "HTTP headers"],
        "C", "Easy"),
    make_mcq(
        "Which templating engine is tightly integrated with Spring MVC for server-side rendering?",
        ["Handlebars", "Thymeleaf", "EJS", "Pug"],
        "B", "Easy"),
    make_mcq(
        "In a React + Spring Boot app, which protocol is primarily used for communication?",
        ["SOAP", "GraphQL", "HTTP/REST", "RMI"],
        "C", "Easy"),
    make_mcq(
        "What command starts a Spring Boot application using Maven?",
        ["mvn start", "mvn spring-boot:run", "mvn deploy", "mvn boot:start"],
        "B", "Easy"),

    # ── MEDIUM (30) ─────────────────────────────────────────────
    make_mcq(
        "Which Spring Security class should be extended to customize security filter chain configuration?",
        ["WebSecurityConfigurerAdapter", "AuthenticationProvider", "SecurityContextHolder", "FilterChainProxy"],
        "A", "Medium"),
    make_mcq(
        "In a JWT-based authentication flow with Spring Security, where is the token typically sent by the SPA?",
        ["As a query parameter", "In the Authorization header as Bearer token", "In a cookie only", "In the request body"],
        "B", "Medium"),
    make_mcq(
        "Which Hibernate annotation is used to configure lazy loading on a collection?",
        ["@Lazy", "@FetchType.LAZY", "@OneToMany(fetch = FetchType.LAZY)", "@LazyLoad"],
        "C", "Medium"),
    make_mcq(
        "What is the purpose of the @CrossOrigin annotation in Spring Boot?",
        ["Enable cross-database queries", "Allow requests from different origins", "Enable cross-module dependency injection", "Support cross-platform deployment"],
        "B", "Medium"),
    make_mcq(
        "Which library is commonly used for mocking dependencies in Spring Boot tests?",
        ["PowerMock", "EasyMock", "Mockito", "WireMock"],
        "C", "Medium"),
    make_mcq(
        "In Spring Boot, what does @Transactional ensure?",
        ["Thread safety", "Atomic database operations with rollback on failure", "REST endpoint security", "Lazy loading of entities"],
        "B", "Medium"),
    make_mcq(
        "Which Spring Boot starter adds support for Spring Data JPA?",
        ["spring-boot-starter-web", "spring-boot-starter-data-jpa", "spring-boot-starter-jdbc", "spring-boot-starter-data-rest"],
        "B", "Medium"),
    make_mcq(
        "What is the role of ModelMapper or MapStruct in a Spring Boot application?",
        ["Database migration", "Object-to-object mapping for DTOs", "HTTP request routing", "Dependency injection"],
        "B", "Medium"),
    make_mcq(
        "In a fullstack Java app, where should CORS be configured if the React app runs on a different port?",
        ["In the React package.json only", "In the Spring Boot backend (e.g., WebMvcConfigurer)", "In the browser settings", "In the database configuration"],
        "B", "Medium"),
    make_mcq(
        "Which annotation in Spring Boot is used to handle exceptions globally across all controllers?",
        ["@ExceptionHandler", "@ControllerAdvice", "@ErrorController", "@ResponseStatus"],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of MockMvc in Spring Boot testing?",
        ["To mock database connections", "To simulate HTTP requests without starting a server", "To mock external API calls", "To test JavaScript frontend code"],
        "B", "Medium"),
    make_mcq(
        "In a Gradle build file, which block defines project dependencies?",
        ["plugins { }", "repositories { }", "dependencies { }", "configurations { }"],
        "C", "Medium"),
    make_mcq(
        "What does the Swagger/OpenAPI @Api annotation do?",
        ["Enables API rate limiting", "Documents a controller for API specification", "Creates API endpoints automatically", "Validates API request payloads"],
        "B", "Medium"),
    make_mcq(
        "Which Spring annotation marks a class to handle data access exceptions and component scanning for repositories?",
        ["@Service", "@Repository", "@Component", "@Controller"],
        "B", "Medium"),
    make_mcq(
        "In a React frontend consuming a Spring Boot API, which React hook is typically used for data fetching on component mount?",
        ["useState", "useEffect", "useContext", "useReducer"],
        "B", "Medium"),
    make_mcq(
        "What is the advantage of using JAR packaging over WAR for Spring Boot apps?",
        ["Smaller file size always", "Includes an embedded server and runs standalone", "Better security by default", "Supports more databases"],
        "B", "Medium"),
    make_mcq(
        "Which Maven plugin is used to create a Docker image for a Spring Boot application?",
        ["maven-compiler-plugin", "spring-boot-maven-plugin", "jib-maven-plugin", "maven-jar-plugin"],
        "C", "Medium"),
    make_mcq(
        "In Spring Security, what is the purpose of the OncePerRequestFilter?",
        ["Execute a filter exactly once per request cycle", "Cache request data", "Handle CORS preflight requests", "Log every request"],
        "A", "Medium"),
    make_mcq(
        "What does @Valid annotation do when used on a controller method parameter?",
        ["Validates that the user is authenticated", "Triggers Bean Validation on the request body", "Validates the HTTP method", "Checks if the endpoint is valid"],
        "B", "Medium"),
    make_mcq(
        "In a Spring Boot + Angular SPA, which side handles client-side routing?",
        ["Spring Boot backend", "Angular frontend (Angular Router)", "Thymeleaf templates", "Apache Tomcat"],
        "B", "Medium"),
    make_mcq(
        "Which annotation in JPA defines the primary key of an entity?",
        ["@Column", "@Id", "@Key", "@PrimaryKey"],
        "B", "Medium"),
    make_mcq(
        "What does the spring-boot-starter-websocket dependency enable?",
        ["HTTP polling", "Server-Sent Events only", "WebSocket and STOMP messaging support", "gRPC communication"],
        "C", "Medium"),
    make_mcq(
        "In a CI/CD pipeline for a Java fullstack app, what does the 'build' stage typically produce?",
        ["Source code zip", "A deployable artifact (JAR/WAR)", "A Git tag", "A test report only"],
        "B", "Medium"),
    make_mcq(
        "Which HTTP status code should a REST API return when a resource is not found?",
        ["400 Bad Request", "401 Unauthorized", "403 Forbidden", "404 Not Found"],
        "D", "Medium"),
    make_mcq(
        "What is the purpose of the @GeneratedValue annotation in JPA?",
        ["Generates REST endpoints", "Auto-generates primary key values", "Creates database tables", "Generates DTO classes"],
        "B", "Medium"),
    make_mcq(
        "In Spring Boot, which profile mechanism allows different configurations for dev and prod?",
        ["@Profile annotation and application-{profile}.properties", "@Environment annotation", "@Mode annotation", "@Config(profile) annotation"],
        "A", "Medium"),
    make_mcq(
        "What is the role of the DispatcherServlet in Spring MVC?",
        ["Manages database transactions", "Acts as the front controller routing requests to handlers", "Handles WebSocket connections", "Manages dependency injection"],
        "B", "Medium"),
    make_mcq(
        "Which caching annotation in Spring Boot caches the result of a method?",
        ["@CacheEvict", "@CachePut", "@Cacheable", "@EnableCaching"],
        "C", "Medium"),
    make_mcq(
        "In a Dockerfile for a Spring Boot app, which base image is commonly used?",
        ["node:alpine", "python:3.9", "openjdk:17-jdk-slim", "nginx:latest"],
        "C", "Medium"),
    make_mcq(
        "What does the @ManyToOne annotation represent in JPA?",
        ["A one-to-one relationship", "Many entities mapping to one parent entity", "A many-to-many relationship", "An inheritance mapping"],
        "B", "Medium"),

    # ── HARD (15) ───────────────────────────────────────────────
    make_mcq(
        "In Spring Security with JWT, what is the correct order of filter chain processing for a stateless API?",
        [
            "Authentication → Authorization → JWT Validation",
            "JWT Validation Filter → UsernamePasswordAuthenticationFilter → Authorization",
            "CORS Filter → CSRF Filter → Basic Auth Filter",
            "Authorization → Authentication → Session Creation"
        ],
        "B", "Hard"),
    make_mcq(
        "What problem does the N+1 select issue cause in Hibernate, and how is it typically resolved?",
        [
            "Duplicate inserts; resolved with @UniqueConstraint",
            "Excessive queries for related entities; resolved with JOIN FETCH or @BatchSize",
            "Transaction deadlocks; resolved with optimistic locking",
            "Memory leaks; resolved with @Cacheable"
        ],
        "B", "Hard"),
    make_mcq(
        "When using Spring WebSocket with STOMP, which broker relay is used for scalable pub/sub messaging?",
        [
            "In-memory SimpleBroker only",
            "An external message broker like RabbitMQ or ActiveMQ",
            "Redis cache as a broker",
            "Kafka Streams"
        ],
        "B", "Hard"),
    make_mcq(
        "In a Spring Boot microservice architecture, what is the purpose of Spring Cloud Gateway?",
        [
            "Manages database connections across services",
            "Provides API gateway with routing, load balancing, and cross-cutting concerns",
            "Handles container orchestration",
            "Acts as a service mesh sidecar"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the difference between @Transactional(propagation = REQUIRES_NEW) and REQUIRED?",
        [
            "REQUIRES_NEW reuses the current transaction; REQUIRED creates a new one",
            "REQUIRES_NEW always creates a new transaction; REQUIRED joins the existing one or creates if none exists",
            "They are identical in behavior",
            "REQUIRED always creates a new transaction; REQUIRES_NEW joins existing"
        ],
        "B", "Hard"),
    make_mcq(
        "How does Spring Boot handle circular dependencies by default, and what changed in Spring Boot 2.6+?",
        [
            "Circular dependencies were always prohibited",
            "They were resolved via setter injection; 2.6+ prohibited circular references by default",
            "They are resolved via constructor injection in all versions",
            "Spring Boot has no mechanism to detect circular dependencies"
        ],
        "B", "Hard"),
    make_mcq(
        "In a React + Spring Boot deployment, what strategy avoids CORS issues entirely in production?",
        [
            "Disabling browser security",
            "Serving the React build as static resources from the Spring Boot JAR or using a reverse proxy",
            "Using HTTP instead of HTTPS",
            "Setting all origins to wildcard in development only"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the purpose of @EntityGraph in Spring Data JPA?",
        [
            "Defines database schema graphs",
            "Provides a declarative way to define fetch plans and override default fetch types",
            "Creates entity relationship diagrams",
            "Graphs query execution performance"
        ],
        "B", "Hard"),
    make_mcq(
        "Which concurrency strategy does Hibernate's @Version annotation implement?",
        [
            "Pessimistic locking with SELECT FOR UPDATE",
            "Optimistic locking using version comparison",
            "Distributed locking via external service",
            "Read-write lock with thread synchronization"
        ],
        "B", "Hard"),
    make_mcq(
        "In a CI/CD pipeline using Docker multi-stage builds for a Java app, what is the primary benefit?",
        [
            "Faster compilation speed",
            "Smaller final image by separating build-time dependencies from runtime",
            "Automatic test execution",
            "Built-in vulnerability scanning"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the key difference between Spring's @Component, @Service, @Repository, and @Controller?",
        [
            "They have completely different functionality",
            "They are all specializations of @Component with semantic meaning and some additional behavior (e.g., exception translation for @Repository)",
            "Only @Component supports dependency injection",
            "@Service and @Repository cannot be used with @Autowired"
        ],
        "B", "Hard"),
    make_mcq(
        "How does Spring Boot DevTools' LiveReload interact with a React frontend during development?",
        [
            "It replaces React Hot Module Replacement entirely",
            "DevTools restarts the backend; the React dev server independently handles frontend hot reload",
            "DevTools compiles React code on the server",
            "LiveReload only works with Thymeleaf, not SPAs"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the purpose of the @Conditional annotations (e.g., @ConditionalOnProperty) in Spring Boot auto-configuration?",
        [
            "To conditionally validate user input",
            "To conditionally register beans based on environment, properties, or classpath conditions",
            "To set conditional breakpoints during debugging",
            "To define conditional REST endpoints"
        ],
        "B", "Hard"),
    make_mcq(
        "In Spring Data JPA, what is the difference between findById() and getOne()/getReferenceById()?",
        [
            "findById() uses lazy loading; getReferenceById() uses eager loading",
            "findById() returns Optional with an actual entity; getReferenceById() returns a lazy proxy",
            "They are identical methods with different names",
            "getReferenceById() queries the cache; findById() always hits the database"
        ],
        "B", "Hard"),
    make_mcq(
        "When implementing HATEOAS in a Spring Boot REST API, which class is used to add hypermedia links to responses?",
        [
            "ResponseEntity only",
            "EntityModel and WebMvcLinkBuilder from Spring HATEOAS",
            "HyperlinkResource from JAX-RS",
            "@LinkedResource annotation"
        ],
        "B", "Hard"),
]

if __name__ == "__main__":
    insert_domain_questions(DOMAIN, questions)
