#!/bin/bash
# Quick deployment script for VPS
# Run this on dify.yourads.io

set -e

echo "🚀 Deploying Adaptive Text Sizing to VPS..."

# Navigate to project directory
cd ~/creo_image_generator || cd /root/creo_image_generator || {
    echo "❌ Error: Could not find project directory"
    echo "Please update this script with the correct path"
    exit 1
}

echo "📥 Pulling latest changes from Git..."
git pull origin main

echo "🏗️  Building and restarting containers..."
./deploy.sh

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🧪 Testing:"
echo "curl http://dify.yourads.io:8000/health"
echo ""
echo "📊 Check logs:"
echo "docker logs creo_image_generator-api-1 --tail 50"
echo ""
