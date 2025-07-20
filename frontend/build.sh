#!/bin/bash

# Exit on any error
set -e

echo "🔧 Installing dependencies..."
yarn install

echo "🏗️ Building application..."
yarn build

echo "✅ Build completed successfully!" 