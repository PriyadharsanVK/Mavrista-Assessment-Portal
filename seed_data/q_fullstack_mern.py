#!/usr/bin/env python3
"""Fullstack Development - MERN: 65 MCQ questions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from seed_data.common import make_mcq, insert_domain_questions

DOMAIN = "Fullstack Development - MERN"

questions = [
    # ── EASY (20) ──────────────────────────────────────────────
    make_mcq(
        "What does MERN stand for?",
        ["MongoDB, Express, React, Node", "MySQL, Express, React, Nginx", "MongoDB, Ember, React, Node", "MongoDB, Express, Redux, Node"],
        "A", "Easy"),
    make_mcq(
        "In MongoDB, data is stored in which format?",
        ["Tables and rows", "BSON (Binary JSON) documents", "XML files", "CSV records"],
        "B", "Easy"),
    make_mcq(
        "Which command initializes a new Node.js project with a package.json?",
        ["node init", "npm init", "npm start", "node create"],
        "B", "Easy"),
    make_mcq(
        "In React, what is JSX?",
        ["A database query language", "A syntax extension that allows writing HTML-like code in JavaScript", "A CSS preprocessor", "A testing framework"],
        "B", "Easy"),
    make_mcq(
        "Which React hook is used to manage component state?",
        ["useEffect", "useState", "useContext", "useRef"],
        "B", "Easy"),
    make_mcq(
        "In Express.js, which method is used to define a route that handles GET requests?",
        ["app.post()", "app.get()", "app.put()", "app.listen()"],
        "B", "Easy"),
    make_mcq(
        "What is Mongoose in the MERN stack?",
        ["A React component library", "An ODM (Object Document Mapper) for MongoDB and Node.js", "A CSS framework", "A test runner"],
        "B", "Easy"),
    make_mcq(
        "Which command installs a package and saves it to package.json dependencies?",
        ["npm install --save-dev <pkg>", "npm install <pkg>", "npm add --global <pkg>", "npm update <pkg>"],
        "B", "Easy"),
    make_mcq(
        "In React, props are used to:",
        ["Manage internal component state", "Pass data from parent to child components", "Style components", "Handle HTTP requests"],
        "B", "Easy"),
    make_mcq(
        "What does the Express middleware express.json() do?",
        ["Sends JSON responses", "Parses incoming JSON request bodies", "Validates JSON schemas", "Compresses JSON data"],
        "B", "Easy"),
    make_mcq(
        "In MongoDB, which method finds all documents in a collection?",
        ["db.collection.findAll()", "db.collection.find()", "db.collection.getAll()", "db.collection.select()"],
        "B", "Easy"),
    make_mcq(
        "What is the virtual DOM in React?",
        ["The actual browser DOM", "A lightweight JavaScript representation of the real DOM for efficient updates", "A server-side rendering engine", "A database abstraction layer"],
        "B", "Easy"),
    make_mcq(
        "Which Node.js module is used to create an HTTP server?",
        ["fs", "path", "http", "os"],
        "C", "Easy"),
    make_mcq(
        "In React Router, which component is used to define a route path?",
        ["<Link>", "<Route>", "<Switch>", "<Navigate>"],
        "B", "Easy"),
    make_mcq(
        "What does npm stand for?",
        ["Node Package Manager", "New Project Module", "Node Process Manager", "Network Protocol Module"],
        "A", "Easy"),
    make_mcq(
        "In Express.js, what does res.json() do?",
        ["Reads a JSON file", "Sends a JSON response to the client", "Parses the request body", "Validates JSON data"],
        "B", "Easy"),
    make_mcq(
        "Which MongoDB method inserts a single document?",
        ["db.collection.add()", "db.collection.insertOne()", "db.collection.create()", "db.collection.save()"],
        "B", "Easy"),
    make_mcq(
        "What is the default port for a React development server created with Create React App?",
        ["8080", "5000", "3000", "4200"],
        "C", "Easy"),
    make_mcq(
        "In Node.js, which keyword is used to import modules using CommonJS?",
        ["import", "require", "include", "load"],
        "B", "Easy"),
    make_mcq(
        "Which React hook is used to perform side effects like data fetching?",
        ["useState", "useMemo", "useEffect", "useCallback"],
        "C", "Easy"),

    # ── MEDIUM (30) ─────────────────────────────────────────────
    make_mcq(
        "In Express.js, what is the purpose of middleware?",
        [
            "Defining database schemas",
            "Functions that execute during the request-response cycle with access to req, res, and next",
            "Compiling React components",
            "Managing environment variables"
        ],
        "B", "Medium"),
    make_mcq(
        "How does React's useContext hook help manage state?",
        [
            "It replaces Redux entirely",
            "It provides a way to pass data through the component tree without prop drilling",
            "It manages server-side state",
            "It handles form validation"
        ],
        "B", "Medium"),
    make_mcq(
        "In MongoDB, what is the aggregation pipeline?",
        [
            "A method to delete multiple documents",
            "A framework for transforming and analyzing data through sequential stages",
            "A way to create indexes",
            "A backup mechanism"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of the .env file in a MERN application?",
        [
            "Defining CSS styles",
            "Storing environment-specific configuration like API keys and database URIs",
            "Listing npm dependencies",
            "Configuring React component structure"
        ],
        "B", "Medium"),
    make_mcq(
        "In JWT authentication, what are the three parts of a JWT token?",
        [
            "Username, password, role",
            "Header, payload, signature",
            "Access token, refresh token, session ID",
            "Public key, private key, certificate"
        ],
        "B", "Medium"),
    make_mcq(
        "What does CORS middleware in Express.js enable?",
        [
            "Database connection pooling",
            "Cross-origin HTTP requests from different domains",
            "Compression of response data",
            "Server-side rendering of React"
        ],
        "B", "Medium"),
    make_mcq(
        "In Mongoose, what does a schema define?",
        [
            "Express routes",
            "The structure, types, and validation rules of documents in a collection",
            "React component props",
            "Node.js module exports"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of React's useReducer hook?",
        [
            "Reduces bundle size",
            "Manages complex state logic with dispatch actions, similar to Redux",
            "Reduces API call frequency",
            "Optimizes rendering performance"
        ],
        "B", "Medium"),
    make_mcq(
        "In Express.js, how do you handle errors globally?",
        [
            "Using try-catch in every route",
            "Defining an error-handling middleware with (err, req, res, next) signature",
            "Using console.error()",
            "Wrapping Express in a Promise"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of the Multer middleware in Express.js?",
        [
            "JSON parsing", "Handling multipart/form-data for file uploads", "CORS configuration", "Authentication"
        ],
        "B", "Medium"),
    make_mcq(
        "In React, what is the key prop used for in lists?",
        [
            "Styling list items",
            "Helping React identify which items have changed, been added, or removed",
            "Setting the index for array methods",
            "Defining event handlers for each item"
        ],
        "B", "Medium"),
    make_mcq(
        "In MongoDB, what does the $lookup stage do in an aggregation pipeline?",
        [
            "Filters documents",
            "Performs a left outer join with another collection",
            "Sorts documents",
            "Groups documents"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the event loop in Node.js?",
        [
            "A for-loop that iterates over events",
            "A mechanism that handles asynchronous operations by offloading tasks and executing callbacks when ready",
            "A React lifecycle method",
            "A MongoDB query operator"
        ],
        "B", "Medium"),
    make_mcq(
        "In a MERN app, where should sensitive API keys be stored?",
        [
            "In the React frontend source code",
            "In server-side environment variables (e.g., .env on the backend)",
            "In the MongoDB database",
            "In the package.json file"
        ],
        "B", "Medium"),
    make_mcq(
        "What is Redux used for in a React application?",
        [
            "Server-side rendering",
            "Centralized and predictable state management across components",
            "Database management",
            "CSS styling"
        ],
        "B", "Medium"),
    make_mcq(
        "In Express.js, what does app.use() do?",
        [
            "Starts the server",
            "Mounts middleware or sub-routers at a specified path",
            "Sends a response",
            "Closes the database connection"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of React.memo()?",
        [
            "Memoizes database queries",
            "Prevents unnecessary re-renders by memoizing a functional component",
            "Creates memos (notes) in the app",
            "Allocates more memory to a component"
        ],
        "B", "Medium"),
    make_mcq(
        "In MongoDB, what is an index and why is it important?",
        [
            "A backup copy of data",
            "A data structure that improves query performance by allowing efficient lookups",
            "A type of document",
            "A collection naming convention"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of PM2 in Node.js deployment?",
        [
            "Package management",
            "A process manager that keeps Node.js apps alive, handles clustering, and manages logs",
            "A testing framework",
            "A database driver"
        ],
        "B", "Medium"),
    make_mcq(
        "In React, what does the useMemo hook do?",
        [
            "Manages form state",
            "Memoizes a computed value to avoid expensive recalculations on every render",
            "Creates a new component instance",
            "Handles side effects"
        ],
        "B", "Medium"),
    make_mcq(
        "How do you implement protected routes in React Router?",
        [
            "Using CSS to hide routes",
            "Creating a wrapper component that checks auth state and redirects if unauthenticated",
            "Using Express middleware in React",
            "Removing routes from the HTML"
        ],
        "B", "Medium"),
    make_mcq(
        "In Express.js, what is the difference between app.get() and router.get()?",
        [
            "They are identical",
            "router.get() creates modular route handlers that can be mounted on the app; app.get() defines routes directly",
            "app.get() is for POST requests; router.get() is for GET requests",
            "router.get() only works with MongoDB"
        ],
        "B", "Medium"),
    make_mcq(
        "In Jest testing, what does the describe() function do?",
        [
            "Defines a test case",
            "Groups related test cases into a test suite",
            "Asserts expected values",
            "Mocks API calls"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of the useCallback hook in React?",
        [
            "Calls an API on mount",
            "Memoizes a callback function to prevent unnecessary re-creation across renders",
            "Creates callback-based routing",
            "Handles error callbacks"
        ],
        "B", "Medium"),
    make_mcq(
        "In MongoDB, which method updates a document and returns the modified version?",
        [
            "updateOne()",
            "findOneAndUpdate() with returnDocument: 'after'",
            "replaceOne()",
            "modifyOne()"
        ],
        "B", "Medium"),
    make_mcq(
        "In a MERN stack deployment, what role does Nginx typically play?",
        [
            "Database server",
            "Reverse proxy for the Node.js backend and static file server for the React build",
            "Package manager",
            "Test runner"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of React Testing Library's render() function?",
        [
            "Renders components on the production server",
            "Renders components into a virtual DOM for testing and returns query utilities",
            "Compiles JSX to JavaScript",
            "Renders CSS styles"
        ],
        "B", "Medium"),
    make_mcq(
        "In Node.js, what is a stream?",
        [
            "A type of variable",
            "An abstract interface for working with data that can be read/written in chunks",
            "A CSS animation",
            "A React component lifecycle"
        ],
        "B", "Medium"),
    make_mcq(
        "What is the purpose of the mongoose.populate() method?",
        [
            "Fills the database with seed data",
            "Replaces ObjectId references with the actual referenced documents",
            "Creates new collections",
            "Populates HTML templates"
        ],
        "B", "Medium"),
    make_mcq(
        "In a MERN app, what is the typical approach for deploying React and Express separately?",
        [
            "Both on the same server process",
            "React on a static host (Vercel/Netlify); Express on a server (Heroku/AWS) with API proxy",
            "React deployed as a MongoDB plugin",
            "Express serves React source files directly"
        ],
        "B", "Medium"),

    # ── HARD (15) ───────────────────────────────────────────────
    make_mcq(
        "In MongoDB, what is the difference between embedding and referencing documents, and when should each be used?",
        [
            "Embedding is always better for all use cases",
            "Embedding stores related data in a single document (good for 1:few); referencing uses ObjectIds across collections (good for 1:many or many:many)",
            "Referencing is the only approach MongoDB supports",
            "Embedding creates separate collections automatically"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the event loop's order of phases in Node.js?",
        [
            "I/O → Timers → Check → Close",
            "Timers → Pending Callbacks → Idle/Prepare → Poll → Check → Close Callbacks",
            "Poll → Timers → Check → I/O",
            "Timers → Poll → Microtasks → Check"
        ],
        "B", "Hard"),
    make_mcq(
        "In React, what is the difference between useEffect cleanup and componentWillUnmount?",
        [
            "They are completely different mechanisms",
            "useEffect cleanup runs before every re-render's effect and on unmount; componentWillUnmount runs only on unmount",
            "componentWillUnmount is called on every render",
            "useEffect cleanup never runs on unmount"
        ],
        "B", "Hard"),
    make_mcq(
        "How does MongoDB's WiredTiger storage engine handle concurrency?",
        [
            "Table-level locking only",
            "Document-level concurrency control with optimistic locking using MVCC",
            "No concurrency support",
            "Global database lock"
        ],
        "B", "Hard"),
    make_mcq(
        "In a MERN application, how do you prevent JWT token theft via XSS attacks?",
        [
            "Store JWT in localStorage; it is always safe",
            "Store JWT in an httpOnly, secure, sameSite cookie so it is inaccessible to JavaScript",
            "Include the JWT in the URL",
            "Encrypt the JWT with a client-side key"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the purpose of React's reconciliation algorithm?",
        [
            "Compiling JSX to HTML",
            "Efficiently determining the minimum number of DOM updates by comparing virtual DOM trees using heuristic diffing",
            "Managing API request queues",
            "Handling Redux state updates"
        ],
        "B", "Hard"),
    make_mcq(
        "In Express.js, how does the middleware chain handle async errors that are not caught?",
        [
            "Express automatically catches all async errors",
            "Unhandled async rejections bypass error middleware; you need express-async-errors or explicit next(err) in catch blocks",
            "Async errors are logged but never crash the server",
            "Express converts async errors to 404 responses"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the difference between process.nextTick() and setImmediate() in Node.js?",
        [
            "They are identical",
            "process.nextTick() fires before any I/O events in the next iteration; setImmediate() fires in the check phase after I/O",
            "setImmediate() is synchronous; process.nextTick() is asynchronous",
            "process.nextTick() is deprecated"
        ],
        "B", "Hard"),
    make_mcq(
        "In MongoDB, how does the aggregation pipeline's $facet stage work?",
        [
            "It creates database indexes",
            "It processes multiple aggregation pipelines within a single stage on the same input documents",
            "It joins two collections",
            "It paginates results"
        ],
        "B", "Hard"),
    make_mcq(
        "In React, what problem does the useRef hook solve that useState cannot?",
        [
            "useRef is faster than useState",
            "useRef persists a mutable value across renders without causing re-renders, useful for DOM references and previous values",
            "useRef replaces useEffect",
            "useRef handles asynchronous state"
        ],
        "B", "Hard"),
    make_mcq(
        "How does Node.js handle CPU-intensive tasks without blocking the event loop?",
        [
            "Node.js cannot handle CPU-intensive tasks",
            "Using Worker Threads, child processes, or offloading to external services/message queues",
            "By increasing the event loop speed",
            "By using synchronous I/O"
        ],
        "B", "Hard"),
    make_mcq(
        "In a MERN stack, what is the purpose of MongoDB change streams?",
        [
            "Migrating data between collections",
            "Allowing applications to listen for real-time data changes in the database using an event-driven approach",
            "Streaming large files to the client",
            "Compressing MongoDB documents"
        ],
        "B", "Hard"),
    make_mcq(
        "What are the implications of React's Strict Mode in development?",
        [
            "It improves production performance",
            "It intentionally double-invokes certain functions (render, effects) to detect side effects and highlights deprecations",
            "It enforces TypeScript usage",
            "It enables server-side rendering"
        ],
        "B", "Hard"),
    make_mcq(
        "In Express.js, how do you implement rate limiting to prevent abuse?",
        [
            "Using res.setTimeout()",
            "Using middleware like express-rate-limit that tracks requests per IP within a time window",
            "By limiting the number of routes",
            "By setting Content-Length headers"
        ],
        "B", "Hard"),
    make_mcq(
        "What is the difference between MongoDB's find() with projection and the $project aggregation stage?",
        [
            "They are identical",
            "find() projection only includes/excludes fields; $project can also create computed fields, rename fields, and reshape documents",
            "$project is slower than find() projection",
            "find() projection supports aggregation expressions"
        ],
        "B", "Hard"),
]

if __name__ == "__main__":
    insert_domain_questions(DOMAIN, questions)
