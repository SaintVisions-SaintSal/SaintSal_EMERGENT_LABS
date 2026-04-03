#!/bin/bash

# Development script for EMERGENT_LABS frontend
# This script navigates to the frontend directory and starts the dev server

set -e

echo "Starting EMERGENT_LABS development server..."

# Navigate to the frontend directory
cd "$(dirname "$0")/../frontend"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    yarn install
fi

# Start the development server
echo "Starting development server on http://localhost:3000"
yarn start
