#! /bin/sh
AUTH0_SERVICE_PORT=8013 AUTH0_SERVICE_IP=172.18.0.2 AUTH0_CLIENT_ID=WSZVdEXnSXBLIto8aCrISMbDWlPw4AOJ \
AUTH0_CLIENT_SECRET=ID1_vdAxx7jsX-S5EpfEz8f1MsonxoHq9MOFG7RMszfclRB8fh4J_-Wum05sXVLV \
REDIS_DB_URL="redis://Gregg.Lebovitz:6UAxEABT6geyV*h@redis-16774.c9.us-east-1-4.ec2.cloud.redislabs.com:16774" \
REDIS_DB_DB="IntelAgent" \
python server.py
