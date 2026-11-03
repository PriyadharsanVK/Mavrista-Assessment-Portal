#!/usr/bin/env python3
"""Fullstack Development - MEAN: 65 MCQ questions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from seed_data.common import make_mcq, insert_domain_questions

DOMAIN = "Fullstack Development - MEAN"

questions = [
    # ── EASY (20) ──────────────────────────────────────────────
    make_mcq(
        "What does MEAN stand for?",
        ["MongoDB, Express, Angular, Node", "MySQL, Express, Angular, Nginx", "MongoDB, Ember, Angular, Node", "MongoDB, Express, AngularJS, Next"],
        "A", "Easy"),
    make_mcq(
        "Which language is Angular primarily written in?",
        ["JavaScript", "TypeScript", "Dart", "CoffeeScript"],
        "B", "Easy"),
    make_mcq(
        "In Angular, what is a component?",
        ["A database table", "A reusable UI building block with a template, class, and metadata", "A Node.js module", "A MongoDB collection"],
        "B", "Easy"),
    make_mcq(
        "What does the Angular CLI command 'ng new' do?",
        ["Creates a new component", "Generates a new Angular project with boilerplate", "Starts the dev server", "Runs unit tests"],
        "B", "Easy"),
    make_mcq(
        "In TypeScript, what is the purpose of an interface?",
        ["Defining CSS styles", "Defining the shape/contract of an object", "Creating database schemas", "Importing modules"],
        "B", "Easy"),
    make_mcq(
        "Which Angular decorator is used to define a component?",
        ["@Injectable", "@Component", "@NgModule", "@Directive"],
        "B", "Easy"),
    make_mcq(
        "In MongoDB with Mongoose, what does a model represent?",
        ["An Express route", "A constructor compiled from a Schema for creating and querying documents", "An Angular service", "A TypeScript type"],
        "B", "Easy"),
    make_mcq(
        "What command starts an Angular development server?",
        ["ng build", "ng serve", "ng start", "ng run"],
        "B", "Easy"),
    make_mcq(
        "In TypeScript, which keyword defines a variable with a fixed type?",
        ["var", "let with type annotation (let x: number)", "const with any", "define"],
        "B", "Easy"),
    make_mcq(
        "What is the purpose of Angular's NgModule?",
        ["Defines CSS styles", "Organizes the application into cohesive blocks of functionality", "Manages database connections", "Handles HTTP requests"],
        "B", "Easy"),
    make_mcq(
        "In Express.js, which method sends an HTTP response with a status code?",
        ["res.json()", "res.status().send()", "res.write()", "res.end()"],
        "B", "Easy"),
    make_mcq(
        "What is the Angular Router used for?",
        ["Database routing", "Navigating between different views/components in a single-page app", "Routing Express API requests", "Managing state"],
        "B", "Easy"),
    make_mcq(
        "In TypeScript, what does the 'any' type represent?",
        ["Only numbers", "A type that allows any value, opting out of type checking", "Only strings", "An error type"],
        "B", "Easy"),
    make_mcq(
        "Which Angular directive repeats an element for each item in a list?",
        ["*ngIf", "*ngFor", "*ngSwitch", "*ngClass"],
        "B", "Easy"),
    make_mcq(
        "In a MEAN stack app, which layer handles HTTP requests from the Angular frontend?",
        ["MongoDB", "Angular services", "Express.js backend", "Node.js core modules"],
        "C", "Easy"),
    make_mcq(
        "What is the purpose of Angular's HttpClient module?",
        ["Managing component state", "Making HTTP requests to backend APIs", "Handling WebSocket connections", "Compiling TypeScript"],
        "B", "Easy"),
    make_mcq(
        "In TypeScript, what is an enum?",
        ["A CSS property", "A set of named constants", "A database query type", "A testing utility"],
        "B", "Easy"),
    make_mcq(
        "Which Node.js feature makes it efficient for I/O-heavy applications?",
        ["Multi-threading by default", "Non-blocking, event-driven architecture", "Built-in GPU support", "Automatic code compilation"],
        "B", "Easy"),
    make_mcq(
        "In Angular, what is data binding?",
        ["Connecting the database to the view", "A mechanism to synchronize data between the component class and the template", "Binding CSS to HTML", "Linking Express routes to Angular"],
        "B", "Easy"),
    make_mcq(
        "What does 'npm run build' typically do in an Angular project?",
        ["Starts the development server", "Compiles the Angular app into static files for production deployment", "Runs unit tests", "Installs dependencies"],
        "B", "Easy"),

    # ── MEDIUM (30) ─────────────────────────────────────────────
    make_mcq(
        "In Angular, what is the difference between template-driven and reactive forms?",
        [
            "They are identical approaches",
            "Template-driven forms use directives in the template; reactive forms use FormGroup/FormControl in the component class",
            "Template-driven forms are for server-side; reactive forms are for client-side",
            "Reactive forms cannot handle validation"
        ],
        "B", "Medium"),
    make_mcq(
        "What is dependency injection in Angular?",
        [
            "A way to inject CSS styles",
            "A design pattern where services are provided to components without manual instantiation",
            "A method to inject SQL queries",
            "A way to inject HTML templates"
        ],
        "B", "Medium"),
    make_mcq(
        "In Angular, what is an Observable from RxJS?",
        [
            "A static variable",
            "A stream of asynchronous data that can be subscribed to for receiving values over time",
            "A database query",
            "A CSS animation"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of Angular interceptors?",
        [
            "Intercepting database queries",
            "Intercepting and modifying HTTP requests or responses globally (e.g., adding auth headers)",
            "Intercepting route changes",
            "Intercepting CSS loading"
        ],
        "B", "Medium"),
    make_mcq(
        "In TypeScript, what is the purpose of generics?",
        [
            "Defining database schemas",
            "Creating reusable components that work with multiple types while maintaining type safety",
            "Generating CSS classes",
            "Handling HTTP responses"
        ],
        "B", "Medium"),
    make_mcq(
        "What are Angular guards used for?",
        [
            "Protecting the database",
            "Controlling access to routes based on conditions like authentication status",
            "Guarding against CSS injection",
            "Preventing server crashes"
        ],
        "B", "Medium"),
    make_mcq(
        "In Angular, what is the purpose of a pipe?",
        [
            "Connecting components",
            "Transforming displayed data in templates (e.g., date formatting, uppercase)",
            "Managing HTTP streams",
            "Creating database pipelines"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the difference between Promises and Observables in Angular?",
        [
            "They are identical",
            "Promises handle a single async value; Observables handle multiple values over time and support operators like map and filter",
            "Observables are synchronous; Promises are asynchronous",
            "Promises support cancellation; Observables do not"
        ],
        "B", "Medium"),
    make_mcq(
        "In TypeScript, what is a type guard?",
        [
            "A security feature",
            "A runtime check that narrows the type of a variable within a conditional block",
            "An Angular route guard",
            "A form validation method"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of Angular's ngOnInit lifecycle hook?",
        [
            "Destroys the component",
            "Initializes the component after Angular sets input properties; ideal for fetching initial data",
            "Handles form submissions",
            "Compiles the template"
        ],
        "B", "Medium"),
    make_mcq(
        "In an Express + Angular MEAN app, how is JWT authentication typically implemented?",
        [
            "Angular generates the JWT token",
            "Express generates the JWT on login; Angular stores it and sends it via an HTTP interceptor in subsequent requests",
            "MongoDB stores active sessions instead",
            "JWT is handled by Angular Router"
        ],
        "B", "Medium"),
    make_mcq(
        "What is NgRx in the Angular ecosystem?",
        [
            "A testing library",
            "A reactive state management library inspired by Redux, using actions, reducers, and selectors",
            "A CSS framework for Angular",
            "An alternative to RxJS"
        ],
        "B", "Medium"),
    make_mcq(
        "In Angular, what does the async pipe do?",
        [
            "Makes HTTP requests",
            "Automatically subscribes to an Observable or Promise and returns the emitted value, handling unsubscription on destroy",
            "Validates async form fields",
            "Runs async JavaScript code"
        ],
        "B", "Medium"),
    make_mcq(
        "In TypeScript, what is the difference between an interface and a type alias?",
        [
            "They are completely interchangeable with no differences",
            "Interfaces support declaration merging and extension; type aliases can define unions, intersections, and mapped types",
            "Type aliases are faster at runtime",
            "Interfaces cannot define object shapes"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of Angular Material?",
        [
            "Database management",
            "A UI component library implementing Material Design for Angular applications",
            "A build tool",
            "A testing framework"
        ],
        "B", "Medium"),
    make_mcq(
        "In Express.js, what is the purpose of the Router class?",
        [
            "Routing database queries",
            "Creating modular, mountable route handlers that can be used as middleware",
            "Routing Angular component navigation",
            "Managing WebSocket connections"
        ],
        "B", "Medium"),
    make_mcq(
        "What are decorators in TypeScript?",
        [
            "CSS style helpers",
            "Special declarations that attach metadata to classes, methods, or properties at design time",
            "Variable naming conventions",
            "Database query builders"
        ],
        "B", "Medium"),
    make_mcq(
        "In Angular, what is the difference between ngOnInit and the constructor?",
        [
            "They are identical",
            "Constructor is for dependency injection setup; ngOnInit is for initialization logic after inputs are set",
            "Constructor runs after ngOnInit",
            "ngOnInit is for CSS initialization"
        ],
        "B", "Medium"),
    make_mcq(
        "How does Angular's change detection mechanism work?",
        [
            "It polls the database for changes",
            "It checks component trees for data changes and updates the DOM when bindings change, triggered by events, timers, or HTTP responses",
            "It only runs when manually triggered",
            "It uses WebSockets"
        ],
        "B", "Medium"),
    make_mcq(
        "In a MEAN stack app, what is the purpose of environment.ts and environment.prod.ts in Angular?",
        [
            "Defining database schemas",
            "Storing environment-specific configuration like API URLs that are swapped during build",
            "Defining Angular routes",
            "Managing npm dependencies"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of the RxJS switchMap operator?",
        [
            "Switches between components",
            "Maps each source emission to an Observable, cancelling the previous inner subscription",
            "Switches database connections",
            "Maps CSS classes"
        ],
        "B", "Medium"),
    make_mcq(
        "In TypeScript, what is the 'unknown' type and how does it differ from 'any'?",
        [
            "They are identical",
            "unknown requires type checking before usage while any bypasses all type checks",
            "unknown is only for strings; any is for numbers",
            "any is stricter than unknown"
        ],
        "B", "Medium"),
    make_mcq(
        "What does the 'ng build --configuration production' command do differently from a dev build?",
        [
            "It skips compilation",
            "It enables AOT compilation, tree-shaking, minification, and uses production environment settings",
            "It runs unit tests",
            "It deploys to a server"
        ],
        "B", "Medium"),
    make_mcq(
        "In Angular, what is a service and how is it typically provided?",
        [
            "A template file",
            "A class decorated with @Injectable that encapsulates business logic, typically provided in root or a specific module",
            "A CSS stylesheet",
            "A routing configuration"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of Jasmine and Karma in Angular testing?",
        [
            "Database testing tools",
            "Jasmine is a BDD testing framework for writing tests; Karma is a test runner that executes them in browsers",
            "Jasmine handles deployment; Karma handles monitoring",
            "They are Angular UI libraries"
        ],
        "B", "Medium"),
    make_mcq(
        "In MongoDB with Mongoose, what is the purpose of middleware (pre/post hooks)?",
        [
            "Defining Express routes",
            "Executing logic before or after certain operations like save, validate, or remove",
            "Handling Angular HTTP requests",
            "Creating database indexes"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of Angular's structural directive *ngIf?",
        [
            "Iterates over a list",
            "Conditionally includes or removes an element from the DOM based on a boolean expression",
            "Applies CSS classes",
            "Handles click events"
        ],
        "B", "Medium"),
    make_mcq(
        "In Express.js, how do you serve the Angular production build as static files?",
        [
            "Using res.render()",
            "Using express.static() middleware pointing to the Angular dist folder",
            "Using app.listen() with Angular path",
            "Angular cannot be served from Express"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the role of Docker in deploying a MEAN stack application?",
        [
            "Replaces MongoDB",
            "Containerizes application components for consistent deployment across environments",
            "Only used for frontend deployment",
            "Manages npm packages"
        ],
        "B", "Medium"),
    make_mcq(
        "In Angular, what is lazy loading of modules?",
        [
            "Loading all modules at startup",
            "Loading feature modules on demand when a route is navigated to, reducing initial bundle size",
            "Lazy evaluation of TypeScript types",
            "Caching API responses"
        ],
        "B", "Medium"),

    # ── HARD (15) ───────────────────────────────────────────────
    make_mcq(
        "In Angular, what is the difference between OnPush and Default change detection strategies?",
        [
            "They are identical",
            "Default checks all components on every change detection cycle; OnPush only checks when inputs change, events fire, or an Observable emits",
            "OnPush is slower than Default",
            "Default only works with reactive forms"
        ],
        "B", "Hard"),
    make_mcq(
        "How does Angular's Ahead-of-Time (AOT) compilation differ from Just-in-Time (JIT)?",
        [
            "AOT is slower in production",
            "AOT compiles templates at build time for faster rendering and smaller bundles; JIT compiles in the browser at runtime",
            "JIT produces smaller bundles than AOT",
            "AOT only works with TypeScript 4+"
        ],
        "B", "Hard"),
    make_mcq(
        "In RxJS, what is the difference between mergeMap, switchMap, concatMap, and exhaustMap?",
        [
            "They are all aliases for the same operator",
            "mergeMap runs inner Observables concurrently; switchMap cancels previous; concatMap queues sequentially; exhaustMap ignores new until current completes",
            "switchMap is synchronous; the others are asynchronous",
            "concatMap cancels all pending subscriptions"
        ],
        "B", "Hard"),
    make_mcq(
        "What is Zone.js and why is it critical to Angular's change detection?",
        [
            "A CSS framework",
            "A library that monkey-patches async APIs to notify Angular when async operations complete, triggering change detection",
            "A database driver",
            "A Node.js clustering tool"
        ],
        "B", "Hard"),
    make_mcq(
        "In TypeScript, how do mapped types work and what is a common use case?",
        [
            "They map database tables to types",
            "They transform properties of an existing type (e.g., Partial<T> makes all properties optional by iterating over keyof T)",
            "They map HTTP routes to handlers",
            "They convert CSS to TypeScript"
        ],
        "B", "Hard"),
    make_mcq(
        "How does Angular's dependency injection hierarchical injector system work?",
        [
            "All services are singletons globally",
            "Each component and module has its own injector; child injectors inherit from parents, allowing scoped service instances",
            "DI only works at the root level",
            "Services cannot be scoped to specific modules"
        ],
        "B", "Hard"),
    make_mcq(
        "In a MEAN stack app, how do you implement real-time updates using Socket.IO with Angular?",
        [
            "Angular's HttpClient handles real-time updates automatically",
            "Create a Socket.IO server in Express; create an Angular service wrapping the socket.io-client to emit/listen for events",
            "Use MongoDB change streams directly in Angular",
            "Real-time updates require React, not Angular"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the purpose of Angular's Renderer2 service?",
        [
            "Rendering database queries",
            "Providing a platform-agnostic way to manipulate DOM elements, enabling server-side rendering and web worker compatibility",
            "Rendering CSS animations",
            "Rendering Express responses"
        ],
        "B", "Hard"),
    make_mcq(
        "In TypeScript, what are conditional types and how do they work?",
        [
            "Types that change based on user input",
            "Types that use extends keyword to select one of two types based on a condition (T extends U ? X : Y)",
            "Types that only work in if-else blocks",
            "A runtime type-checking mechanism"
        ],
        "B", "Hard"),
    make_mcq(
        "How does tree-shaking work in Angular's production build and what enables it?",
        [
            "It removes unused CSS classes",
            "Webpack/esbuild statically analyzes ES module imports to eliminate unused code; Angular's AOT compilation enables effective tree-shaking",
            "It only removes unused npm packages",
            "Angular does not support tree-shaking"
        ],
        "B", "Hard"),
    make_mcq(
        "In Angular, what is the purpose of content projection using ng-content?",
        [
            "Projecting database content",
            "Allowing a parent component to pass arbitrary template content into a child component's designated slots",
            "Loading external CSS content",
            "Projecting images onto the screen"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the difference between Angular's ViewChild and ContentChild?",
        [
            "They are identical",
            "ViewChild queries elements in the component's own template; ContentChild queries elements projected via ng-content from a parent",
            "ViewChild is for services; ContentChild is for components",
            "ContentChild works only with pipes"
        ],
        "B", "Hard"),
    make_mcq(
        "In a production MEAN deployment, how do you handle Angular routing with Express to prevent 404 on deep links?",
        [
            "Define every Angular route in Express",
            "Add a catch-all Express route that serves index.html for any route not matching an API endpoint",
            "Disable Angular Router",
            "Use hash-based routing only"
        ],
        "B", "Hard"),
    make_mcq(
        "In TypeScript, what is declaration merging and how does it apply to interfaces?",
        [
            "Combining multiple files into one",
            "When multiple interface declarations with the same name are automatically merged into a single definition",
            "Merging TypeScript with JavaScript files",
            "It only works with classes, not interfaces"
        ],
        "B", "Hard"),
    make_mcq(
        "How does Angular's Ivy rendering engine improve performance compared to the View Engine?",
        [
            "Ivy is slower but more feature-rich",
            "Ivy uses incremental DOM, enables better tree-shaking, faster compilation, smaller bundles, and improved debugging",
            "Ivy only works with JIT compilation",
            "View Engine supports AOT but Ivy does not"
        ],
        "B", "Hard"),
]

if __name__ == "__main__":
    insert_domain_questions(DOMAIN, questions)
