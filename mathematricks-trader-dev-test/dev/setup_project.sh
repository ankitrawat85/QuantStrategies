#!/bin/bash

# Mathematricks Trader - Development Environment Setup Script
# This script sets up everything needed to run the project locally

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.11"
VENV_DIR="venv"
MONGO_DB_NAME="mathematricks_trading"
COLLECTIONS_DIR="./dev/downloads/exported_collections"

echo ""
echo "=========================================="
echo "  Mathematricks Trader Setup Script"
echo "=========================================="
echo ""

# Check for MongoDB
echo ""
echo -e "${BLUE}[2/7] Checking MongoDB installation...${NC}"
echo ""

if ! command -v mongod &> /dev/null; then
    echo -e "${YELLOW}⚠️  MongoDB not found. Installing MongoDB Community Edition...${NC}"

    # Add MongoDB tap
    brew tap mongodb/brew

    # Install MongoDB
    brew install mongodb-community

    echo -e "${GREEN}✅ MongoDB installed${NC}"
else
    MONGO_VER=$(mongod --version | head -n 1)
    echo -e "${GREEN}✅ MongoDB installed: ${MONGO_VER}${NC}"
fi

# Check if MongoDB is running
echo ""
echo -e "${BLUE}[3/7] Checking MongoDB service...${NC}"
echo ""

if pgrep -x "mongod" > /dev/null; then
    echo -e "${GREEN}✅ MongoDB is running${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB is not running. Starting MongoDB...${NC}"
    brew services start mongodb-community

    # Wait for MongoDB to start
    echo "Waiting for MongoDB to start..."
    sleep 3

    if pgrep -x "mongod" > /dev/null; then
        echo -e "${GREEN}✅ MongoDB started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start MongoDB. Please start it manually:${NC}"
        echo "   brew services start mongodb-community"
        exit 1
    fi
fi

# Check MongoDB connection
if mongosh --quiet --eval "db.version()" &> /dev/null; then
    echo -e "${GREEN}✅ MongoDB connection successful${NC}"
else
    echo -e "${RED}❌ Cannot connect to MongoDB. Please check MongoDB status.${NC}"
    exit 1
fi


# Import MongoDB collections
echo ""
echo -e "${BLUE}[6/7] Importing MongoDB collections...${NC}"
echo ""

if [ -d "$COLLECTIONS_DIR" ]; then
    # Find the latest exported files
    LATEST_FILES=$(ls -t "$COLLECTIONS_DIR"/*.json 2>/dev/null | head -4)

    if [ -z "$LATEST_FILES" ]; then
        echo -e "${YELLOW}⚠️  No exported collection files found in ${COLLECTIONS_DIR}${NC}"
        echo "Skipping MongoDB import. You'll need to set up collections manually."
    else
        echo "Found exported collections. Checking which need to be imported..."

        for file in $LATEST_FILES; do
            collection=$(basename "$file" | sed 's/_[0-9]*\.json$//')

            # Check if collection exists and has documents
            doc_count=$(mongosh --quiet "$MONGO_DB_NAME" --eval "db.${collection}.countDocuments({})" 2>/dev/null || echo "0")

            if [ "$doc_count" -gt 0 ]; then
                echo -e "  ${BLUE}ℹ️  ${collection}: Already exists with ${doc_count} documents (skipping)${NC}"
            else
                echo "  Importing: $collection"
                mongoimport \
                    --db="$MONGO_DB_NAME" \
                    --collection="$collection" \
                    --file="$file" \
                    --jsonArray \
                    --quiet

                if [ $? -eq 0 ]; then
                    new_count=$(mongosh --quiet "$MONGO_DB_NAME" --eval "db.${collection}.countDocuments({})")
                    echo -e "    ${GREEN}✅ Imported ${new_count} documents${NC}"
                else
                    echo -e "    ${RED}❌ Failed to import ${collection}${NC}"
                fi
            fi
        done
    fi
else
    echo -e "${YELLOW}⚠️  Collections directory not found: ${COLLECTIONS_DIR}${NC}"
    echo "You'll need to set up MongoDB collections manually."
fi

# Create .env file if it doesn't exist
echo ""
echo -e "${BLUE}[7/7] Checking configuration files...${NC}"
echo ""

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating template...${NC}"

    cat > .env <<EOF
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/?replicaSet=rs0

# GCP Configuration (for Pub/Sub)
GCP_PROJECT_ID=mathematricks-trader
GCP_CREDENTIALS_PATH=path/to/credentials.json

# Service Configuration
DEFAULT_ACCOUNT_ID=Mock_Paper

# Environment
ENVIRONMENT=development
EOF

    echo -e "${GREEN}✅ Created .env template${NC}"
    echo -e "${YELLOW}⚠️  Please update .env with your actual credentials${NC}"
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Deactivate virtual environment
deactivate
