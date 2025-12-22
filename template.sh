#!/bin/bash

# List of outer-level folders
folders=(
  "artifact"
  "components"
  "constants"
  "datasets"
  "entity"
  "logger"
  "pipeline"
  "notebook"
  "exceptions"
)

# Create folders and __init__.py inside each
for folder in "${folders[@]}"; do
  mkdir -p "$folder"
  touch "$folder/__init__.py"
done

# Create root-level files
touch .env
touch README.md

echo "✅ OmniTask AI base structure created successfully."
