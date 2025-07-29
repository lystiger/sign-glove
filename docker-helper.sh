#!/bin/bash

# Sign Glove Docker Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    print_status "Docker is running"
}

# Function to start the stack
start_stack() {
    print_header "Starting Sign Glove Stack"
    check_docker
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp env.example .env
        print_status "Please edit .env file with your configuration"
    fi
    
    print_status "Building and starting containers..."
    docker-compose up -d --build
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "Checking service health..."
    docker-compose ps
    
    print_status "Stack is ready!"
    echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
    echo -e "${GREEN}Backend:${NC} http://localhost:8080"
    echo -e "${GREEN}API Docs:${NC} http://localhost:8080/docs"
}

# Function to stop the stack
stop_stack() {
    print_header "Stopping Sign Glove Stack"
    docker-compose down
    print_status "Stack stopped"
}

# Function to restart the stack
restart_stack() {
    print_header "Restarting Sign Glove Stack"
    stop_stack
    start_stack
}

# Function to view logs
view_logs() {
    print_header "Viewing Logs"
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$1"
    fi
}

# Function to clean up
cleanup() {
    print_header "Cleaning Up Docker"
    print_warning "This will remove all containers, networks, and images!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        docker system prune -a --volumes -f
        print_status "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show status
show_status() {
    print_header "Stack Status"
    docker-compose ps
    
    echo
    print_header "Resource Usage"
    docker stats --no-stream
    
    echo
    print_header "Disk Usage"
    docker system df
}

# Function to access containers
access_container() {
    if [ -z "$1" ]; then
        print_error "Please specify a service (backend, frontend, mongodb)"
        exit 1
    fi
    
    print_status "Accessing $1 container..."
    docker-compose exec "$1" bash
}

# Function to backup database
backup_db() {
    print_header "Backing Up Database"
    BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    docker-compose exec mongodb mongodump --out /backup
    docker cp "$(docker-compose ps -q mongodb):/backup" "$BACKUP_DIR"
    
    print_status "Backup saved to $BACKUP_DIR"
}

# Function to restore database
restore_db() {
    if [ -z "$1" ]; then
        print_error "Please specify backup directory"
        exit 1
    fi
    
    print_header "Restoring Database"
    print_warning "This will overwrite existing data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker cp "$1" "$(docker-compose ps -q mongodb):/backup"
        docker-compose exec mongodb mongorestore /backup
        print_status "Database restored"
    else
        print_status "Restore cancelled"
    fi
}

# Function to show help
show_help() {
    echo "Sign Glove Docker Helper Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start       Start the entire stack"
    echo "  stop        Stop the entire stack"
    echo "  restart     Restart the entire stack"
    echo "  logs [SERVICE] View logs (all or specific service)"
    echo "  status      Show stack status and resource usage"
    echo "  shell SERVICE Access container shell"
    echo "  backup      Backup database"
    echo "  restore DIR Restore database from backup"
    echo "  cleanup     Clean up Docker (remove everything)"
    echo "  help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs backend"
    echo "  $0 shell frontend"
    echo "  $0 backup"
}

# Main script logic
case "${1:-help}" in
    start)
        start_stack
        ;;
    stop)
        stop_stack
        ;;
    restart)
        restart_stack
        ;;
    logs)
        view_logs "$2"
        ;;
    status)
        show_status
        ;;
    shell)
        access_container "$2"
        ;;
    backup)
        backup_db
        ;;
    restore)
        restore_db "$2"
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 