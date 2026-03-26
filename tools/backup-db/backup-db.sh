#!/bin/bash
#
# Simple PostgreSQL Backup & Restore Script
#
# Usage:
#   ./backup_db.sh backup
#   ./backup_db.sh restore <backup_file>
#   ./backup_db.sh list
#
# Configuration via environment variables:
#   DB_HOST       (default: localhost)
#   DB_PORT       (default: 5432)
#   DB_USER       (default: postgres)
#   DB_PASSWORD   (required for auth)
#   DB_NAME       (required)
#

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Config
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.sql"

# Get settings from environment
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME="${DB_NAME:-}"

# Show help
show_help() {
    cat << EOF
PostgreSQL Backup & Restore

Usage:
  ./backup_db.sh backup    Create a backup
  ./backup_db.sh restore   Restore from backup
  ./backup_db.sh list      List available backups

Environment Variables:
  DB_HOST      PostgreSQL host (default: localhost)
  DB_PORT      PostgreSQL port (default: 5432)
  DB_USER      PostgreSQL user (default: postgres)
  DB_PASSWORD  PostgreSQL password (required)
  DB_NAME      Database name (required)

Examples:
  export DB_HOST=104.198.103.26
  export DB_USER=nes_user
  export DB_PASSWORD=wDoytBbQNeJWW7I7y1ySCdpD5t09vrgBqqS15qsV8E
  export DB_NAME=nes_db
  
  ./backup_db.sh backup
  ./backup_db.sh list
  ./backup_db.sh restore ./backups/backup_20260326_082002.sql

EOF
}

# Backup function
backup() {
    if [[ -z "$DB_NAME" ]]; then
        echo -e "${RED}Error: DB_NAME environment variable not set${NC}"
        return 1
    fi
    
    mkdir -p "$BACKUP_DIR"
    
    echo -e "${GREEN}Creating backup...${NC}"
    echo "  Host: $DB_HOST"
    echo "  Database: $DB_NAME"
    echo "  File: $BACKUP_FILE"
    echo ""
    
    # Set password for pg_dump
    if [[ -n "$DB_PASSWORD" ]]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi
    
    # Run pg_dump
    if pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -F custom \
        -f "$BACKUP_FILE" \
        -v 2>&1 | grep -v "^Command line"; then
        
        local size=$(du -h "$BACKUP_FILE" | cut -f1)
        echo ""
        echo -e "${GREEN}✓ Backup created: $BACKUP_FILE ($size)${NC}"
    else
        echo -e "${RED}✗ Backup failed${NC}"
        rm -f "$BACKUP_FILE"
        unset PGPASSWORD
        return 1
    fi
    
    unset PGPASSWORD
}

# Restore function
restore() {
    local file="$1"
    
    if [[ -z "$file" ]]; then
        echo -e "${RED}Error: Backup file required${NC}"
        echo "Usage: ./backup_db.sh restore <backup_file>"
        return 1
    fi
    
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}Error: File not found: $file${NC}"
        return 1
    fi
    
    if [[ -z "$DB_NAME" ]]; then
        echo -e "${RED}Error: DB_NAME environment variable not set${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}⚠️  WARNING: This will restore your database!${NC}"
    echo "  Host: $DB_HOST"
    echo "  Database: $DB_NAME"
    echo "  File: $file"
    echo ""
    read -p "Type 'YES' to continue: " -r confirm
    
    if [[ "$confirm" != "YES" ]]; then
        echo "Cancelled."
        return 0
    fi
    
    echo -e "${GREEN}Restoring...${NC}"
    
    # Set password for pg_restore
    if [[ -n "$DB_PASSWORD" ]]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi
    
    # Run pg_restore
    if pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --data-only \
        --no-owner \
        --clean \
        -v \
        "$file" 2>&1 | grep -v "^Command line"; then
        
        echo ""
        echo -e "${GREEN}✓ Restore completed${NC}"
    else
        echo -e "${RED}✗ Restore failed${NC}"
        unset PGPASSWORD
        return 1
    fi
    
    unset PGPASSWORD
}

# List function
list_backups() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        echo "No backups directory found: $BACKUP_DIR"
        return 0
    fi
    
    local count=$(find "$BACKUP_DIR" -maxdepth 1 -name "backup_*.sql" -type f 2>/dev/null | wc -l)
    
    if [[ $count -eq 0 ]]; then
        echo "No backups found in $BACKUP_DIR"
        return 0
    fi
    
    echo -e "${GREEN}Backups ($count):${NC}"
    ls -lhS "$BACKUP_DIR"/backup_*.sql 2>/dev/null | awk '{printf "  %s  %8s\n", $9, $5}'
}

# Main
case "${1:-help}" in
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    list)
        list_backups
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
