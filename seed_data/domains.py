#!/usr/bin/env python3
"""Domain seeder for the 33 assessment domains."""
import sqlite3
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "assessment.sqlite3"

DOMAINS_SPEC = [
    # 1-25: Software Domains
    ("Python", "Software", "Python programming, object-oriented concepts, asynchronous patterns, and standard library.", "🐍"),
    ("Java", "Software", "Core Java, JVM internals, multithreading, collections, Streams, and memory management.", "☕"),
    ("SQL", "Software", "Relational database modeling, complex JOINs, window functions, indexing, and query optimization.", "🗄️"),
    ("C", "Software", "Low-level C programming, pointers, manual memory management, bitwise operations, and data structures.", "⚙️"),
    ("Machine Learning", "Software", "Supervised and unsupervised algorithms, regularization, loss functions, and model evaluation.", "🤖"),
    ("Prompt Engineering", "Software", "Advanced prompt design, Few-Shot, Chain-of-Thought, ReAct framework, and hallucination control.", "💬"),
    ("Generative AI (GenAI)", "Software", "Transformer architecture, LLM fine-tuning (LoRA, PEFT), RAG, embeddings, and vector databases.", "✨"),
    ("Agentic AI", "Software", "Autonomous agent architectures, tool calling, memory systems, planning, and multi-agent coordination.", "🧠"),
    ("Data Science", "Software", "Exploratory data analysis, statistical hypothesis testing, data wrangling, and predictive modeling.", "🔬"),
    ("Data Analytics", "Software", "Business intelligence, KPI tracking, dimensional modeling, cohort analysis, and executive dashboards.", "📊"),
    ("Backend Development - Java", "Software", "Spring Boot architecture, Spring Data JPA, Spring Security, microservices, and REST API design.", "☕"),
    ("Backend Development - Python", "Software", "FastAPI, Django, async programming, SQLAlchemy, caching, background tasks, and API security.", "🐍"),
    ("Fullstack Development - Java", "Software", "End-to-end web engineering with Spring Boot backend, modern frontend SPA, and secure API integration.", "🌐"),
    ("Fullstack Development - Python", "Software", "Fullstack architecture combining Django / FastAPI with modern JavaScript frontends.", "🌐"),
    ("Fullstack Development - MERN", "Software", "Fullstack JavaScript with MongoDB, Express.js, React.js, and Node.js.", "⚛️"),
    ("Fullstack Development - MEAN", "Software", "Fullstack TypeScript development with MongoDB, Express.js, Angular, and Node.js.", "🅰️"),
    ("Vibe Coding", "Software", "AI-assisted agile software construction, rapid prototyping, conversational debugging, and LLM scaffolding.", "⚡"),
    ("Power BI", "Software", "Power BI Desktop, Power Query, DAX measures, dimensional modeling, and report governance.", "📈"),
    ("Tableau", "Software", "Tableau visualizations, calculated fields, LOD expressions, parameters, and interactive dashboards.", "📉"),
    ("UI/UX Design", "Software", "Design thinking, wireframing, WCAG accessibility, typography, design systems, and usability testing.", "🎨"),
    ("Cybersecurity Fundamentals", "Software", "CIA triad, network security, cryptography, OWASP Top 10, penetration testing, and zero-trust.", "🛡️"),
    ("Cloud Computing", "Software", "Cloud architectures, virtualization, VPC networking, storage, serverless, and IAM policies across clouds.", "☁️"),
    ("Manual Testing", "Software", "Software testing life cycle (STLC), test scenarios, boundary value analysis, regression, and bug management.", "🧪"),
    ("Automation Testing - Java", "Software", "Selenium WebDriver with Java, TestNG, Page Object Model, Cucumber BDD, and CI/CD integration.", "🔍"),
    ("Automation Testing - Python", "Software", "Pytest framework, Playwright / Selenium with Python, API testing with requests, and automated test runners.", "🔍"),

    # 26-33: Electrical / Electronics Domains
    ("PCB Design & Development", "Electrical / Electronics", "Schematic capture, layer stackup, impedance control, DRC, thermal reliefs, and Gerber file generation.", "🔌"),
    ("Arduino & Microcontroller Systems", "Electrical / Electronics", "Microcontroller architecture, ATmega328P, timers, interrupts, ADC, PWM, UART, I2C, and SPI protocols.", "📟"),
    ("IoT Hardware Development", "Electrical / Electronics", "IoT hardware architectures, ESP32/ESP8266, LoRa, sensor conditioning, power gating, and wireless edge nodes.", "📡"),
    ("Electronics Circuit Design & Simulation", "Electrical / Electronics", "Analog & digital circuits, BJT/MOSFET biasing, Op-Amps, SPICE simulation, and active filter design.", "⚡"),
    ("VLSI Design Fundamentals", "Electrical / Electronics", "CMOS fabrication, static timing analysis (STA), stick diagrams, Verilog HDL synthesis, and ASIC/FPGA flows.", "🔲"),
    ("Digital Electronics Design", "Electrical / Electronics", "Boolean algebra, K-maps, multiplexers, sequential flip-flops, counters, shift registers, and finite state machines.", "🔢"),
    ("Electronic Product Design", "Electrical / Electronics", "End-to-end hardware product engineering, enclosure IP ratings, thermal design, EMC/EMI compliance, and reliability.", "📱"),
    ("Electronics Quality & Six Sigma", "Electrical / Electronics", "Six Sigma DMAIC, process capability (Cp/Cpk), SPC charts, IPC-A-610 inspection, and quality assurance.", "🎯"),
]

def seed_domains():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    now_stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    
    domain_map = {}
    for name, cat, desc, icon in DOMAINS_SPEC:
        cur.execute("SELECT id FROM domains WHERE name = ? COLLATE NOCASE", (name,))
        row = cur.fetchone()
        if row:
            domain_id = row[0]
            cur.execute("UPDATE domains SET category=?, description=?, icon=?, status='Active' WHERE id=?", 
                        (cat, desc, icon, domain_id))
        else:
            cur.execute("INSERT INTO domains(name, category, description, icon, status, created_at) VALUES(?, ?, ?, ?, 'Active', ?)",
                        (name, cat, desc, icon, now_stamp))
            domain_id = cur.lastrowid
        domain_map[name] = domain_id
    
    con.commit()
    con.close()
    print(f"Successfully configured and verified all {len(domain_map)} domains.")
    return domain_map

if __name__ == "__main__":
    m = seed_domains()
    for k, v in m.items():
        print(f"  [{v}] {k}")

