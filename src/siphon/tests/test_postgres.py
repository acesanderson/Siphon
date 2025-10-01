#!/usr/bin/env python3
import socket
import psycopg2
import os

def test_postgres():
   # Test connection detection
   endpoints = ["localhost", "10.0.0.82", "68.47.92.102"]
   
   for host in endpoints:
       try:
           socket.create_connection((host, 5432), timeout=1).close()
           print(f"✅ Found PostgreSQL at {host}")
           
           # Test actual database connection
           conn = psycopg2.connect(
               dbname="siphon", host=host, port="5432", 
               user="bianders", password=os.getenv("POSTGRES_PASSWORD")
           )
           cursor = conn.cursor()
           cursor.execute("SELECT version();")
           print(f"✅ Database connected: {cursor.fetchone()[0][:50]}...")
           conn.close()
           return
       except Exception as e:
           print(f"❌ {host}: {e}")
   
   print("❌ No PostgreSQL server found")

if __name__ == "__main__":
   test_postgres()
