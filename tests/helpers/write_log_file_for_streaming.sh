#!/usr/bin/env bash
# Write log file that can be streamed
PWDDIR=$(pwd)
echo "start" > "$PWDDIR/log.txt"
for i in {1..100}   # you can also use {0..9}
do
  echo "line $i" >> "$PWDDIR/log.txt"
  sleep 1
done
echo "--- ODTP COMPONENT ENDING ---" >> "$PWDDIR/log.txt"