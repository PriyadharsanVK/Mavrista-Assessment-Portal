#!/usr/bin/env python3
"""Comprehensive System Verification Script for Assessment Portal."""
import json
import sqlite3
import os
import sys

def run_checks():
    print("=================================================================")
    print("       ASSESSMENT PORTAL - COMPREHENSIVE VERIFICATION REPORT     ")
    print("=================================================================")

    con = sqlite3.connect("data/assessment.sqlite3")
    cur = con.cursor()

    # 1. Database Integrity
    print("\n--- 1. DATABASE & SCHEMA INTEGRITY ---")
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"Total Tables: {len(tables)} -> {', '.join(tables)}")
    
    # 2. Domain & Question Pools
    print("\n--- 2. DOMAINS & QUESTION POOL VERIFICATION ---")
    domains = cur.execute("""
        SELECT d.id, d.name, d.category, count(q.id) as q_count
        FROM domains d
        LEFT JOIN questions q ON q.domain_id = d.id
        WHERE d.name != 'General' AND d.name != 'Java Full Stack'
        GROUP BY d.id
        ORDER BY d.id
    """).fetchall()

    print(f"Target Domains Count: {len(domains)} (Expected: 33)")
    software_count = sum(1 for d in domains if d[2] == 'Software')
    elec_count = sum(1 for d in domains if d[2] == 'Electrical / Electronics')
    print(f"  - Software Domains: {software_count} (Expected: 25)")
    print(f"  - Electrical / Electronics Domains: {elec_count} (Expected: 8)")

    all_in_range = True
    for d in domains:
        in_range = 60 <= d[3] <= 80
        if not in_range:
            all_in_range = False
        print(f"  [{d[0]:2d}] {d[1]:<40} | Cat: {d[2]:<24} | Qs: {d[3]} [{'PASS' if in_range else 'FAIL'}]")

    print(f"\nAll 33 domains meet 60-80 question quota: {'YES (100% PASS)' if all_in_range else 'NO'}")

    # 3. Coding Question Rules Verification
    print("\n--- 3. CODING QUESTIONS POOL & TESTCASE RULES ---")
    coding_qs = cur.execute("SELECT id, title, data_json FROM questions WHERE type='Coding'").fetchall()
    print(f"Total Coding Challenges Available: {len(coding_qs)}")
    for q in coding_qs:
        data = json.loads(q[2])
        samples = len(data.get('sampleTests', []))
        hiddens = len(data.get('hiddenTests', []))
        langs = data.get('languages', [])
        valid = (samples == 3 and hiddens == 15)
        print(f"  - {q[0]}: '{q[1][:45]}...'")
        print(f"      Sample Tests: {samples} (Req: 3) | Hidden Tests: {hiddens} (Req: 15) | Valid: {valid}")
        print(f"      Supported Languages: {', '.join(langs)}")

    # 4. MCQ Question Quality Sampling
    print("\n--- 4. MCQ OPTIONS & ANSWER KEY INTEGRITY ---")
    mcq_sample = cur.execute("SELECT id, title, data_json FROM questions WHERE type='MCQ' ORDER BY random() LIMIT 5").fetchall()
    for q in mcq_sample:
        data = json.loads(q[2])
        opts = data.get('options', [])
        correct = data.get('correctOption', '')
        print(f"  - [{q[0]}] {q[1][:60]}...")
        print(f"      Options ({len(opts)}): {opts}")
        print(f"      Correct Answer: {correct} -> Option value: '{opts[ord(correct)-65] if correct in ('A','B','C','D') else 'INVALID'}'")

    # 5. User & Admin Account Check
    print("\n--- 5. ADMIN & AUTHENTICATION AUDIT ---")
    admins = cur.execute("SELECT id, name, email, role, status FROM users WHERE role='admin'").fetchall()
    print(f"Active Administrator Accounts: {len(admins)}")
    for a in admins:
        print(f"  - Admin: {a[1]} | Email: {a[2]} | ID: {a[0]} | Status: {a[4]}")

    con.close()
    print("\n=================================================================")
    print("                     VERIFICATION COMPLETE                       ")
    print("=================================================================")

if __name__ == "__main__":
    run_checks()

