"""
Offline knowledge base.

Curated, verified answers for common developer / programming questions so the
chat stays useful even when no AI provider API key is configured. Every answer
is hand-written and fact-checked; this module NEVER generates new content.

Matching is keyword based. Each topic has primary terms (weight 2) and optional
secondary terms (weight 1). A query must reach the configured score threshold.
"""

import re
from typing import List, Optional

_TOPICS: List[dict] = [
    {
        "primary": ["inheritance", "java inheritance"],
        "secondary": ["java", "extends", "super class", "subclass", "oop"],
        "answer": (
            "## Inheritance in Java\n\n"
            "Inheritance lets one class **reuse** fields and methods of another. "
            "The class that is inherited from is the **parent/super class**; the class that inherits is the "
            "**child/sub class**, created with the `extends` keyword.\n\n"
            "```java\n"
            "class Animal {\n"
            "    void speak() { System.out.println(\"Some sound\"); }\n"
            "}\n"
            "\n"
            "class Dog extends Animal {\n"
            "    void speak() { System.out.println(\"Woof\"); }   // overrides parent\n"
            "}\n"
            "\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Animal a = new Dog();\n"
            "        a.speak(); // prints \"Woof\" (runtime polymorphism)\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "Key points:\n"
            "- Java supports **single inheritance** for classes (a class can extend only one class), "
            "but a class can implement many `interface`s.\n"
            "- Every class implicitly extends `java.lang.Object`.\n"
            "- The `super` keyword refers to the parent: `super.method()` or `super(args)` in a constructor.\n"
            "- Java does **not** support multiple inheritance of classes to avoid the diamond problem; "
            "interfaces provide the workaround.\n\n"
            "## Why inheritance exists\n"
            "- **Code reuse** — shared logic lives in the parent.\n"
            "- **Polymorphism** — a `Dog` can be treated as an `Animal`.\n"
            "- **Extensibility** — new behaviour by overriding methods."
        ),
    },
    {
        "primary": ["polymorphism"],
        "secondary": ["java", "override", "overload", "oop", "dynamic"],
        "answer": (
            "## Polymorphism in Java\n\n"
            "Polymorphism means **one name, many forms** — the same method call behaves differently "
            "depending on the object it is called on.\n\n"
            "### Compile-time (method overloading)\n"
            "Same method name, different parameters:\n"
            "```java\n"
            "int add(int a, int b) { return a + b; }\n"
            "int add(int a, int b, int c) { return a + b + c; }\n"
            "```\n\n"
            "### Runtime (method overriding)\n"
            "A subclass redefines a parent method; the JVM calls the *actual* object's version:\n"
            "```java\n"
            "Animal a = new Dog();\n"
            "a.speak(); // Dog's version runs\n"
            "```\n\n"
            "Why it matters: you can write code against a general type (`Animal`) and have it work "
            "for every subclass, which is the basis of frameworks, collections, and interfaces."
        ),
    },
    {
        "primary": ["encapsulation"],
        "secondary": ["java", "getter", "setter", "private", "oop", "abstraction"],
        "answer": (
            "## Encapsulation in Java\n\n"
            "Encapsulation bundles **data and the methods that operate on it** and hides internal state "
            "behind a controlled interface.\n\n"
            "Standard pattern — fields are `private`, access goes through `public` getters/setters:\n"
            "```java\n"
            "public class Account {\n"
            "    private double balance;\n\n"
            "    public double getBalance() { return balance; }\n"
            "    public void deposit(double amount) {\n"
            "        if (amount > 0) balance += amount;\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "Benefits: protects data from invalid changes, keeps the internal representation free to "
            "change without breaking callers, and is a core pillar of OOP."
        ),
    },
    {
        "primary": ["abstraction"],
        "secondary": ["java", "abstract", "interface", "oop"],
        "answer": (
            "## Abstraction in Java\n\n"
            "Abstraction hides **implementation details** and exposes only what the caller needs. "
            "In Java it is achieved with `abstract` classes and `interface`s.\n\n"
            "```java\n"
            "interface Shape {\n"
            "    double area(); // no body — details are abstract\n"
            "}\n\n"
            "class Circle implements Shape {\n"
            "    private double r;\n"
            "    Circle(double r) { this.r = r; }\n"
            "    public double area() { return Math.PI * r * r; }\n"
            "}\n"
            "```\n\n"
            "- An **abstract class** can have both concrete and abstract methods; a subclass must "
            "implement the abstract ones (or be abstract itself).\n"
            "- An **interface** (Java 8+) can have default/static methods but traditionally declares "
            "only the contract.\n"
            "- Abstraction is about *what* something does; encapsulation is about *how* state is hidden."
        ),
    },
    {
        "primary": ["jvm", "jdk", "jre", "java virtual machine"],
        "secondary": ["java", "bytecode", "compile", "portable", "memory"],
        "answer": (
            "## JVM, JRE and JDK\n\n"
            "- **JDK** (Java Development Kit) = compiler (`javac`), tools, and the JRE. Needed to *develop*.\n"
            "- **JRE** (Java Runtime Environment) = JVM + core libraries. Needed to *run* compiled code.\n"
            "- **JVM** (Java Virtual Machine) = the engine that executes **bytecode** (`MyClass.class`).\n\n"
            "How it works:\n"
            "```text\n"
            "Hello.java  --javac-->  Hello.class (bytecode)  --JVM-->  machine code\n"
            "```\n"
            "The bytecode is platform-independent, which is why Java is *write once, run anywhere* — "
            "each platform ships its own JVM. The JVM also manages memory (heap, stack, garbage "
            "collection) and threads."
        ),
    },
    {
        "primary": ["exception", "checked", "unchecked", "try catch", "try-catch"],
        "secondary": ["java", "error", "throw", "throws", "finally"],
        "answer": (
            "## Exceptions in Java\n\n"
            "Exceptions interrupt normal flow when something goes wrong. Structure:\n"
            "```java\n"
            "try {\n"
            "    int x = Integer.parseInt(input);\n"
            "} catch (NumberFormatException e) {\n"
            "    System.out.println(\"Not a number: \" + e.getMessage());\n"
            "} finally {\n"
            "    // always runs, e.g. closing a resource\n"
            "}\n"
            "```\n\n"
            "- **Checked exceptions** (e.g. `IOException`) must be handled or declared with `throws`.\n"
            "- **Unchecked exceptions** (e.g. `NullPointerException`, `ArithmeticException`) extend "
            "`RuntimeException` and don't need declaration.\n"
            "- `finally` runs whether or not an exception occurred.\n"
            "- `throws` declares that a method may raise an exception; `throw` raises one explicitly.\n"
            "- **Never** catch an exception and do nothing — always log or recover."
        ),
    },
    {
        "primary": ["collection", "arraylist", "hashmap", "hashset", "linkedlist"],
        "secondary": ["java", "list", "set", "map", "framework"],
        "answer": (
            "## Java Collections\n\n"
            "The Collections Framework provides data-structure interfaces and implementations:\n\n"
            "| Interface | Common implementations | Ordered? | Allows duplicates? |\n"
            "|---|---|---|---|\n"
            "| `List` | `ArrayList`, `LinkedList` | Yes | Yes |\n"
            "| `Set` | `HashSet`, `LinkedHashSet`, `TreeSet` | No | No |\n"
            "| `Map` | `HashMap`, `LinkedHashMap`, `TreeMap` | Keys: no | Keys: no |\n\n"
            "```java\n"
            "List<String> names = new ArrayList<>();\n"
            "names.add(\"Ada\");\n"
            "\n"
            "Map<String, Integer> ages = new HashMap<>();\n"
            "ages.put(\"Ada\", 36);\n"
            "ages.get(\"Ada\"); // 36\n"
            "\n"
            "Set<Integer> ids = new HashSet<>();\n"
            "ids.add(1); ids.add(1); // size is 1\n"
            "```\n\n"
            "- `ArrayList` — fast random access, backed by an array; grows automatically.\n"
            "- `LinkedList` — fast insert/delete at ends, slower random access.\n"
            "- `HashMap` — average O(1) get/put based on `hashCode()`.\n"
            "- `TreeSet`/`TreeMap` — sorted, O(log n) operations."
        ),
    },
    {
        "primary": ["thread", "multithreading", "threading", "concurrency"],
        "secondary": ["java", "runnable", "synchronized", "race", "deadlock", "future"],
        "answer": (
            "## Threads & concurrency in Java\n\n"
            "A **thread** is a lightweight unit of execution running inside the same process.\n\n"
            "Two ways to create one:\n"
            "```java\n"
            "// 1. Implement Runnable\n"
            "Thread t1 = new Thread(() -> System.out.println(\"Hello\"));\n"
            "t1.start();\n"
            "\n"
            "// 2. Extend Thread (less preferred)\n"
            "class Worker extends Thread {\n"
            "    public void run() { System.out.println(\"Working\"); }\n"
            "}\n"
            "```\n\n"
            "Key concepts:\n"
            "- `synchronized` / locks protect shared state from **race conditions**.\n"
            "- **Deadlock** happens when threads wait on each other's locks forever.\n"
            "- The Executor framework (`Executors.newFixedThreadPool(...)`) is preferred over raw "
            "threads for managing pools.\n"
            "- `volatile` and the `java.util.concurrent` package (`ConcurrentHashMap`, `BlockingQueue`) "
            "make concurrent code safer."
        ),
    },
    {
        "primary": ["fibonacci"],
        "secondary": ["java", "program", "recursion", "write", "print", "sequence", "code"],
        "answer": (
            "## Java program to print the Fibonacci sequence\n\n"
            "```java\n"
            "public class Fibonacci {\n"
            "    public static void main(String[] args) {\n"
            "        int n = 10; // print first 10 numbers\n"
            "        long a = 0, b = 1;\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            System.out.print(a + \" \");\n"
            "            long next = a + b;\n"
            "            a = b;\n"
            "            b = next;\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "Output: `0 1 1 2 3 5 8 13 21 34`\n\n"
            "Recursive version (clean but O(2^n)):\n"
            "```java\n"
            "static long fib(int n) {\n"
            "    return n <= 1 ? n : fib(n - 1) + fib(n - 2);\n"
            "}\n"
            "```\n"
            "For large `n`, use the iterative loop or memoization instead."
        ),
    },
    {
        "primary": ["list vs tuple", "list and tuple"],
        "secondary": ["python", "mutable", "immutable", "difference", "tuple"],
        "answer": (
            "## List vs Tuple in Python\n\n"
            "- A **list** is **mutable** — you can add, remove, or change items.\n"
            "- A **tuple** is **immutable** — once created it cannot change.\n\n"
            "```python\n"
            "lst = [1, 2, 3]\n"
            "lst.append(4)      # ok\n"
            "\n"
            "tup = (1, 2, 3)\n"
            "# tup.append(4)    # AttributeError\n"
            "```\n\n"
            "Use a **tuple** for fixed data (coordinates, function arguments, dictionary keys) — it is "
            "slightly faster and acts as a hashable, read-only value. Use a **list** when the size or "
            "contents change."
        ),
    },
    {
        "primary": ["list comprehension", "list comprehensions"],
        "secondary": ["python", "loop", "filter", "syntax"],
        "answer": (
            "## Python list comprehensions\n\n"
            "A concise way to build a list from an iterable:\n"
            "```python\n"
            "squares = [x * x for x in range(10)]       # [0, 1, 4, ..., 81]\n"
            "evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]\n"
            "```\n\n"
            "Equivalent to:\n"
            "```python\n"
            "squares = []\n"
            "for x in range(10):\n"
            "    squares.append(x * x)\n"
            "```\n\n"
            "You can also use **dictionary** and **set** comprehensions:\n"
            "```python\n"
            "{k: v for k, v in pairs}   # dict\n"
            "{x % 3 for x in range(10)}  # set\n"
            "```\n"
            "Keep them readable — if the logic gets long, prefer a normal loop or a generator."
        ),
    },
    {
        "primary": ["generator", "yield"],
        "secondary": ["python", "iterator", "memory", "lazy"],
        "answer": (
            "## Python generators\n\n"
            "A generator yields values **lazily**, one at a time, without storing the whole sequence "
            "in memory.\n\n"
            "```python\n"
            "def countdown(n):\n"
            "    while n > 0:\n"
            "        yield n\n"
            "        n -= 1\n"
            "\n"
            "for x in countdown(3):\n"
            "    print(x)  # 3 2 1\n"
            "```\n\n"
            "- A function containing `yield` is a generator function; calling it returns a generator object.\n"
            "- Generators are single-use iterators and are ideal for large or infinite sequences.\n"
            "- A generator expression: `(x * x for x in range(10))`."
        ),
    },
    {
        "primary": ["decorator"],
        "secondary": ["python", "wrapper", "function", "functional"],
        "answer": (
            "## Python decorators\n\n"
            "A decorator is a function that wraps another function to add behaviour without changing "
            "its code.\n\n"
            "```python\n"
            "def timing(fn):\n"
            "    def wrapper(*args, **kwargs):\n"
            "        import time\n"
            "        t = time.perf_counter()\n"
            "        result = fn(*args, **kwargs)\n"
            "        print(f\"{fn.__name__} took {time.perf_counter() - t:.4f}s\")\n"
            "        return result\n"
            "    return wrapper\n"
            "\n"
            "@timing\n"
            "def work():\n"
            "    ...\n"
            "```\n\n"
            "`@timing` is sugar for `work = timing(work)`. Python ships with useful built-ins like "
            "`@staticmethod`, `@classmethod`, `@property`, and `@functools.wraps` (which preserves the "
            "original function's metadata)."
        ),
    },
    {
        "primary": ["gil", "global interpreter lock"],
        "secondary": ["python", "thread", "multithreading", "performance", "concurrency"],
        "answer": (
            "## The Python GIL\n\n"
            "The **Global Interpreter Lock** allows only one thread to execute Python bytecode at a time "
            "inside a single process.\n\n"
            "- Consequences: pure-Python threads don't speed up CPU-bound work; they still help with "
            "**I/O-bound** tasks (network, disk) because the lock is released during blocking I/O.\n"
            "- Workarounds for CPU-bound parallelism: the `multiprocessing` module (separate processes, "
            "each with its own interpreter) or libraries that release the GIL (NumPy, C extensions).\n"
            "- Since Python 3.13 the GIL can be disabled at build time (free-threaded builds), though "
            "it remains the default."
        ),
    },
    {
        "primary": ["python vs java", "java vs python"],
        "secondary": ["difference", "compare", "which", "language"],
        "answer": (
            "## Python vs Java\n\n"
            "| Aspect | Python | Java |\n"
            "|---|---|---|\n"
            "| Typing | Dynamic, duck-typed | Static, explicit |\n"
            "| Syntax | Concise, minimal boilerplate | Verbose |\n"
            "| Compilation | Interpreted (bytecode) | Compiled to JVM bytecode |\n"
            "| Speed | Slower (often) | Faster (JIT) |\n"
            "| Best for | Scripting, data science, ML, quick apps | Large enterprise systems, Android |\n\n"
            "Neither is strictly \"better\" — Python prioritises developer speed and flexibility; Java "
            "prioritises performance, tooling, and long-term maintainability at scale."
        ),
    },
    {
        "primary": ["big o", "big-o", "complexity", "time complexity", "space complexity"],
        "secondary": ["algorithm", "asymptotic", "performance", "o(1)", "o(n)", "o(log n)"],
        "answer": (
            "## Big-O complexity\n\n"
            "Big-O describes how an algorithm's runtime (or memory) grows as the input size `n` grows — "
            "the dominant term, ignoring constants.\n\n"
            "Common classes, fastest → slowest:\n"
            "- **O(1)** — constant: array index lookup, `HashMap.get` (average).\n"
            "- **O(log n)** — logarithmic: binary search, balanced-tree operations.\n"
            "- **O(n)** — linear: scanning a list once.\n"
            "- **O(n log n)** — linearithmic: efficient sorting (Merge sort, Quick sort).\n"
            "- **O(n²)** — quadratic: nested loops, bubble/selection sort.\n"
            "- **O(2ⁿ)** — exponential: naive Fibonacci recursion; unusable for large `n`.\n\n"
            "Example: finding an item in an *unsorted* list is O(n); in a *sorted* list via binary "
            "search it is O(log n)."
        ),
    },
    {
        "primary": ["recursion"],
        "secondary": ["algorithm", "function", "base case", "stack", "recursive"],
        "answer": (
            "## Recursion\n\n"
            "Recursion is when a function calls itself to solve a smaller version of the same problem.\n\n"
            "```python\n"
            "def factorial(n):\n"
            "    if n <= 1:      # base case — stops the recursion\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
            "```\n\n"
            "Every recursive function needs:\n"
            "1. A **base case** that returns without recursing.\n"
            "2. A **recursive case** that moves toward the base case.\n\n"
            "Recursion is elegant for trees, graphs, and divide-and-conquer. Watch out for **stack "
            "overflow** with very deep recursion — Python and Java have recursion-depth limits."
        ),
    },
    {
        "primary": ["nullpointerexception", "null pointer exception"],
        "secondary": ["java", "debug", "error", "fix", "crash"],
        "answer": (
            "## Fixing NullPointerException (Java)\n\n"
            "An `NPE` is thrown when you call a method or access a field on `null`.\n\n"
            "Debugging steps:\n"
            "1. Read the stack trace — it names the exact line.\n"
            "2. Check which variable could be `null` there (often an uninitialised field or a missing "
            "value from a map/DB/JSON parse).\n"
            "3. Add a guard or use `Objects.requireNonNull(...)`.\n\n"
            "```java\n"
            "if (user != null && user.getEmail() != null) {\n"
            "    send(user.getEmail());\n"
            "}\n"
            "```\n"
            "Or use `Optional`: `Optional.ofNullable(user).map(User::getEmail)`. Recent JDKs also print "
            "the exact null variable name in the message."
        ),
    },
    {
        "primary": ["indexoutofboundsexception", "array index out of bounds"],
        "secondary": ["java", "array", "error", "list", "fix"],
        "answer": (
            "## ArrayIndexOutOfBoundsException\n\n"
            "Thrown when you access an index outside the valid range `0 .. length-1`.\n\n"
            "```java\n"
            "int[] a = {10, 20, 30};\n"
            "a[3]; // ERROR — max valid index is 2\n"
            "```\n\n"
            "Fixes: loop with `< a.length`, not `<=`; validate input before indexing; remember "
            "`String.length()` vs array `.length` vs `List.size()`."
        ),
    },
    {
        "primary": ["stackoverflow", "stack overflow error", "stackoverflowerror"],
        "secondary": ["java", "recursion", "infinite", "error", "debug"],
        "answer": (
            "## StackOverflowError\n\n"
            "A `StackOverflowError` (or Python `RecursionError`) means the call stack is full — almost "
            "always **unbounded recursion**: the base case is never reached, or the recursion is "
            "genuinely too deep.\n\n"
            "Fixes:\n"
            "1. Verify the base case is correct and the arguments actually approach it.\n"
            "2. Convert the recursion to an **iterative loop** or use **memoization**.\n"
            "3. Increase the stack size only as a last resort (`-Xss` on the JVM) — fixing the "
            "algorithm is the real solution."
        ),
    },
    {
        "primary": ["sql", "query"],
        "secondary": ["select", "insert", "update", "delete", "database", "table"],
        "answer": (
            "## SQL basics\n\n"
            "Structured Query Language manages relational databases.\n\n"
            "```sql\n"
            "-- Read data\n"
            "SELECT name, age FROM users WHERE age >= 18 ORDER BY name;\n"
            "\n"
            "-- Insert\n"
            "INSERT INTO users (name, age) VALUES ('Ada', 36);\n"
            "\n"
            "-- Update\n"
            "UPDATE users SET age = 37 WHERE name = 'Ada';\n"
            "\n"
            "-- Delete\n"
            "DELETE FROM users WHERE name = 'Ada';\n"
            "```\n\n"
            "Clause order: `SELECT ... FROM ... JOIN ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... "
            "LIMIT ...`. `WHERE` filters rows; `HAVING` filters groups."
        ),
    },
    {
        "primary": ["join"],
        "secondary": ["sql", "inner", "left", "right", "full", "table", "database"],
        "answer": (
            "## SQL JOINs\n\n"
            "A `JOIN` combines rows from two tables on a related column.\n\n"
            "```sql\n"
            "SELECT u.name, o.total\n"
            "FROM users u\n"
            "INNER JOIN orders o ON o.user_id = u.id;\n"
            "```\n\n"
            "- **INNER JOIN** — only matching rows in both tables.\n"
            "- **LEFT JOIN** — all rows from the left table, plus matches; unmatched right side is `NULL`.\n"
            "- **RIGHT JOIN** — mirror of LEFT.\n"
            "- **FULL OUTER JOIN** — all rows from both sides.\n"
            "- **CROSS JOIN** — every combination.\n\n"
            "Use table aliases (`u`, `o`) for readability, and index the join columns for performance."
        ),
    },
    {
        "primary": ["index", "indexes", "indexing"],
        "secondary": ["sql", "database", "performance", "primary key", "unique"],
        "answer": (
            "## Database indexes\n\n"
            "An index is a data structure (usually a B-tree) that lets the database find rows faster "
            "than scanning the whole table.\n\n"
            "```sql\n"
            "CREATE INDEX idx_users_email ON users (email);\n"
            "```\n\n"
            "- Queries using indexed columns in `WHERE`/`JOIN`/`ORDER BY` become much faster.\n"
            "- Costs: extra storage and slower inserts/updates (the index must be maintained).\n"
            "- `PRIMARY KEY` and `UNIQUE` constraints create indexes automatically.\n"
            "- Indexes help most when the column is **selective** (many distinct values)."
        ),
    },
    {
        "primary": ["normalization", "normalisation"],
        "secondary": ["sql", "database", "design", "3nf", "redundancy"],
        "answer": (
            "## Database normalization\n\n"
            "Normalization removes redundancy so data is stored consistently and updates don't "
            "introduce inconsistencies.\n\n"
            "- **1NF** — atomic values, no repeating groups.\n"
            "- **2NF** — 1NF, plus no partial dependency on part of a composite key.\n"
            "- **3NF** — 2NF, plus no transitive dependency (non-key column depending on another "
            "non-key column).\n\n"
            "In practice most systems target **3NF** for transactional data, then *denormalize* "
            "selectively for read-heavy reporting/analytics."
        ),
    },
    {
        "primary": ["rest api", "restful", "rest api design"],
        "secondary": ["http", "get", "post", "put", "delete", "endpoint", "json", "api"],
        "answer": (
            "## REST API basics\n\n"
            "REST is an architectural style where clients interact with resources over HTTP.\n\n"
            "| HTTP method | Purpose |\n"
            "|---|---|\n"
            "| GET | Read a resource |\n"
            "| POST | Create a resource |\n"
            "| PUT / PATCH | Replace / partially update |\n"
            "| DELETE | Remove |\n\n"
            "Design guidelines:\n"
            "- Use **nouns** for resources, not verbs: `GET /users/42`, not `GET /getUser`.\n"
            "- Use plural nouns consistently (`/users`).\n"
            "- Use HTTP status codes: 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, "
            "404 Not Found, 500 Internal Server Error.\n"
            "- Keep it **stateless** — each request carries everything the server needs.\n"
            "- Version APIs (`/v1/users`) when breaking changes are expected."
        ),
    },
    {
        "primary": ["http", "https"],
        "secondary": ["protocol", "request", "response", "status code", "web"],
        "answer": (
            "## HTTP basics\n\n"
            "HTTP is the request/response protocol of the web.\n\n"
            "- **Request** = method (`GET`, `POST`, ...) + URL + headers + optional body.\n"
            "- **Response** = status line + headers + body.\n\n"
            "Common status codes:\n"
            "- 200 OK — success.\n"
            "- 301/302 — redirect.\n"
            "- 400 — bad request; 401 — unauthorized; 403 — forbidden; 404 — not found.\n"
            "- 500 — server error; 502/503 — gateway/service unavailable.\n\n"
            "**HTTPS** wraps HTTP in TLS so the data is encrypted and the server is authenticated. "
            "Statelessness is handled via headers like `Cookie` / `Authorization`."
        ),
    },
    {
        "primary": ["json"],
        "secondary": ["parse", "serialize", "data", "api", "format"],
        "answer": (
            "## JSON\n\n"
            "JSON (JavaScript Object Notation) is the standard text format for exchanging data.\n\n"
            "```json\n"
            "{\n"
            "  \"name\": \"Ada\",\n"
            "  \"age\": 36,\n"
            "  \"skills\": [\"Python\", \"Java\"],\n"
            "  \"active\": true,\n"
            "  \"address\": null\n"
            "}\n"
            "```\n\n"
            "Types: objects `{...}`, arrays `[...]`, strings, numbers, booleans, `null`. "
            "Python: `json.dumps` to serialize, `json.loads` to parse. Java: Jackson or Gson. "
            "JavaScript: `JSON.stringify` / `JSON.parse`."
        ),
    },
    {
        "primary": ["react"],
        "secondary": ["component", "state", "hook", "jsx", "props", "frontend"],
        "answer": (
            "## React basics\n\n"
            "React is a JavaScript library for building UI from **components** — functions returning "
            "JSX that describes the screen.\n\n"
            "```jsx\n"
            "function Counter() {\n"
            "  const [count, setCount] = React.useState(0);\n"
            "  return <button onClick={() => setCount(count + 1)}>{count}</button>;\n"
            "}\n"
            "```\n\n"
            "Key ideas:\n"
            "- **Props** — data passed *into* a component (read-only).\n"
            "- **State** — data a component owns; changes trigger re-render.\n"
            "- **Hooks** (`useState`, `useEffect`, `useContext`) add state and side effects to "
            "function components.\n"
            "- React re-renders when props or state change; use keys in lists and keep components small."
        ),
    },
    {
        "primary": ["git", "github"],
        "secondary": ["commit", "branch", "merge", "push", "pull", "clone", "version control"],
        "answer": (
            "## Git basics\n\n"
            "Git is a version-control system; GitHub hosts remote copies for collaboration.\n\n"
            "```bash\n"
            "git clone <url>            # copy a repo\n"
            "git status                 # what changed\n"
            "git add .                  # stage changes\n"
            "git commit -m \"message\"    # save a snapshot\n"
            "git push origin main       # upload commits\n"
            "git pull                   # download changes\n"
            "git branch feature         # new branch\n"
            "git checkout feature       # switch to it\n"
            "```\n\n"
            "- Commit **early and often**, with clear messages.\n"
            "- Resolve **merge conflicts** by editing the marked sections, then `git add` + commit.\n"
            "- Never commit secrets; use `.gitignore`."
        ),
    },
    {
        "primary": ["oop", "object oriented", "object-oriented programming"],
        "secondary": ["class", "object", "encapsulation", "inheritance", "polymorphism", "abstraction"],
        "answer": (
            "## Object-Oriented Programming\n\n"
            "OOP models software as **objects** — bundles of data (fields) and behaviour (methods) — "
            "grouped into **classes**.\n\n"
            "The four pillars:\n"
            "1. **Encapsulation** — hide internal state behind a controlled interface.\n"
            "2. **Inheritance** — reuse and extend behaviour from a parent class.\n"
            "3. **Polymorphism** — one interface, many implementations; the same call behaves "
            "differently per object.\n"
            "4. **Abstraction** — expose the contract, hide implementation details.\n\n"
            "```python\n"
            "class Dog:\n"
            "    def speak(self):\n"
            "        return \"Woof\"\n"
            "\n"
            "class Cat:\n"
            "    def speak(self):\n"
            "        return \"Meow\"\n"
            "\n"
            "for a in [Dog(), Cat()]:\n"
            "    print(a.speak())\n"
            "```\n"
            "OOP shines when state and behaviour belong together and the system is large enough to "
            "benefit from structure."
        ),
    },
    {
        "primary": ["data structure", "data structures"],
        "secondary": ["array", "linked list", "stack", "queue", "hashmap", "algorithm"],
        "answer": (
            "## Common data structures\n\n"
            "- **Array** — contiguous elements, O(1) random access, O(n) insert/delete.\n"
            "- **Linked list** — nodes pointing to next; O(1) insert/delete at known positions, "
            "O(n) access.\n"
            "- **Stack** — LIFO; push/pop O(1).\n"
            "- **Queue** — FIFO; enqueue/dequeue O(1).\n"
            "- **Hash map / dictionary** — key → value with average O(1) get/put.\n"
            "- **Binary search tree** — sorted, O(log n) average operations.\n"
            "- **Heap** — priority queue; min/max at top, O(log n) push/pop.\n\n"
            "Choosing the right structure for the operations your algorithm does most is the core "
            "of efficient code."
        ),
    },
    {
        "primary": ["binary search", "binary tree", "tree"],
        "secondary": ["algorithm", "data structure", "search", "recursion"],
        "answer": (
            "## Binary search & trees\n\n"
            "**Binary search** finds an item in a sorted array in O(log n) by repeatedly halving the "
            "search range:\n"
            "```python\n"
            "def binary_search(a, target):\n"
            "    lo, hi = 0, len(a) - 1\n"
            "    while lo <= hi:\n"
            "        mid = (lo + hi) // 2\n"
            "        if a[mid] == target: return mid\n"
            "        if a[mid] < target: lo = mid + 1\n"
            "        else: hi = mid - 1\n"
            "    return -1\n"
            "```\n\n"
            "A **binary search tree** keeps nodes ordered (left < node < right), giving O(log n) "
            "search/insert on average — O(n) worst case unless balanced (AVL, Red-Black)."
        ),
    },
    {
        "primary": ["javascript", "js"],
        "secondary": ["web", "frontend", "function", "variable", "es6"],
        "answer": (
            "## JavaScript essentials\n\n"
            "JavaScript adds interactivity to web pages and runs in every browser (and on servers via "
            "Node.js).\n\n"
            "```js\n"
            "// let / const (block-scoped)\n"
            "const name = 'Ada';\n"
            "let count = 0;\n"
            "\n"
            "// arrow function\n"
            "const double = (x) => x * 2;\n"
            "\n"
            "// array methods\n"
            "const nums = [1, 2, 3].map(double);  // [2, 4, 6]\n"
            "const even = nums.filter((n) => n % 2 === 0);\n"
            "```\n\n"
            "Key concepts: closures, promises/`async`-`await`, the DOM, event handling, and `==` vs "
            "`===` (prefer `===`)."
        ),
    },
]


def _score_topic(topic: dict, low: str) -> int:
    score = 0
    for term in topic["primary"]:
        if term in low:
            score += 2
    for term in topic["secondary"]:
        if term in low:
            score += 1
    return score


def lookup(message: str) -> Optional[str]:
    """Return a knowledge-base answer if the message clearly matches a topic."""
    low = re.sub(r"\s+", " ", message.strip().lower())
    if not low:
        return None

    best_topic = None
    best_score = 0
    for topic in _TOPICS:
        score = _score_topic(topic, low)
        if score > best_score:
            best_score = score
            best_topic = topic

    # A clear match needs at least one primary term (weight 2) or two secondary terms.
    if best_topic is None or best_score < 2:
        return None

    answer = best_topic["answer"]
    if best_topic.get("mode"):
        answer = f"*{best_topic['mode']}*\n\n{answer}"
    return answer
