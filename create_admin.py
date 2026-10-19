#!/usr/bin/env python3
"""Create the first or an additional administrator without putting passwords in shell history."""
import getpass
import re
import secrets
import sys

import server

def main():
    email=input('Admin email: ').strip()
    name=input('Admin name: ').strip()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):
        print('Enter a valid email address.',file=sys.stderr);return 2
    password=getpass.getpass('Password (12+ characters): ')
    confirm=getpass.getpass('Confirm password: ')
    if password!=confirm:
        print('Passwords do not match.',file=sys.stderr);return 2
    try: encoded=server.password_hash(password)
    except ValueError as exc:
        print(exc,file=sys.stderr);return 2
    server.init_db()
    con=server.db()
    try:
        admin_id='ADM-'+secrets.token_hex(5)
        con.execute('INSERT INTO users(id,role,name,email,password_hash,created_at) VALUES(?,?,?,?,?,?)',
                    (admin_id,'admin',name or 'Administrator',email,encoded,server.stamp()))
    except Exception as exc:
        print(f'Could not create administrator: {exc}',file=sys.stderr);return 1
    print(f'Administrator created: {email} ({admin_id})')
    return 0

if __name__=='__main__': raise SystemExit(main())
