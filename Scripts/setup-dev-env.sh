#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Starting development environment setup..."
#fetch a name for the project
read -p "Enter the name of the project: " PROJECT_NAME

# Check for package manager
print_warning "Checking for package manager..."

if command -v apt &> /dev/null; then
    PKG="apt"
    INSTALL_CMD="sudo apt install -y"
elif command -v yum &> /dev/null; then
    PKG="yum"
    INSTALL_CMD="sudo yum install -y"
elif command -v dnf &> /dev/null; then
    PKG="dnf"
    INSTALL_CMD="sudo dnf install -y"
elif command -v zypper &> /dev/null; then
    PKG="zypper"
    INSTALL_CMD="sudo zypper install -y"
else
    echo "no package manager found (apt/yum/dnf/zypper)"
    exit 1
fi

print_status "Using package manager: $PKG"
print_warning "Checking for required tools..."

# Check for required tools if not exists install them 
list=("git" "docker" "docker-compose" "python" "node.js" "npm" "vscode")

for tool in "${list[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        print_error "Tool $tool is not installed."
        print_warning "Installing $tool..."
        sudo $PKG install "$tool" -y
    fi
    print_status "$tool is installed."
done
print_status "All required tools are installed."

print_status "Creating a directory for the project..."
# make sure you run the script from the root of the project
mkdir "$PROJECT_NAME"
cd "$PROJECT_NAME"  
mkdir Frontend Backend Database Docs Scripts 
touch .gitignore

print_status "Project directory created successfully."
print_status "Development environment setup completed."
