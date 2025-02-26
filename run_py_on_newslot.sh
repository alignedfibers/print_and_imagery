#!/bin/bash
echo "$@" | nc -U /tmp/python_process_engine.sock

