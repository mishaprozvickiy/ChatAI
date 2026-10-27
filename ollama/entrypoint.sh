#!/bin/bash
set -e

ollama serve &
OLLAMA_PID=$!

until curl -s http://localhost:11434 > /dev/null; do
    sleep 1
done

ollama pull qwen2.5:7b
wait $OLLAMA_PID