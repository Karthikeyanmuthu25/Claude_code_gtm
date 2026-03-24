#!/bin/bash

# AI GTM Content System - Installation Script
# Installs multi-subagent LinkedIn content pipeline for Claude Code

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_msg "Checking prerequisites..."
    
    # Check for Claude Code
    if ! command -v claude &> /dev/null; then
        print_warning "Claude Code CLI not found in PATH"
        print_msg "If Claude Code is installed but not in PATH, you can continue"
        print_msg "Or install from: https://docs.claude.com/en/docs/claude-code/overview"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "Claude Code found"
    fi
    
    # Check Node.js version
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
        if [ "$NODE_VERSION" -ge 20 ]; then
            print_success "Node.js $NODE_VERSION found"
        else
            print_warning "Node.js 20+ recommended, found version $NODE_VERSION"
        fi
    else
        print_warning "Node.js not found"
        print_msg "Claude Code requires Node.js 20+"
    fi
}

# Create directories
setup_directories() {
    print_msg "Setting up Claude Code directories..."
    
    CLAUDE_DIR="$HOME/.claude"
    AGENTS_DIR="$CLAUDE_DIR/agents"
    COMMANDS_DIR="$CLAUDE_DIR/commands"
    
    mkdir -p "$AGENTS_DIR"
    mkdir -p "$COMMANDS_DIR"
    
    print_success "Directories created at $CLAUDE_DIR"
}

# Install subagents
install_agents() {
    print_msg "Installing subagents..."
    
    # Copy subagent files
    cp research-agent.md "$AGENTS_DIR/content-researcher.md"
    print_success "Installed content-researcher"
    
    cp writer-agent.md "$AGENTS_DIR/content-writer.md"
    print_success "Installed content-writer"
    
    cp qa-agent.md "$AGENTS_DIR/content-qa.md"
    print_success "Installed content-qa"
    
    cp optimizer-agent.md "$AGENTS_DIR/content-optimizer.md"
    print_success "Installed content-optimizer"
}

# Install orchestrator command
install_command() {
    print_msg "Installing orchestrator command..."
    
    cp content-pipeline-command.md "$COMMANDS_DIR/content-pipeline.md"
    print_success "Installed /content-pipeline command"
}

# Verify installation
verify_installation() {
    print_msg "Verifying installation..."
    
    # Check agents
    AGENT_COUNT=$(ls -1 "$AGENTS_DIR"/content-*.md 2>/dev/null | wc -l)
    if [ "$AGENT_COUNT" -eq 4 ]; then
        print_success "All 4 subagents installed"
    else
        print_error "Expected 4 subagents, found $AGENT_COUNT"
        return 1
    fi
    
    # Check command
    if [ -f "$COMMANDS_DIR/content-pipeline.md" ]; then
        print_success "Orchestrator command installed"
    else
        print_error "Orchestrator command not found"
        return 1
    fi
    
    # List installed components
    print_msg "Installed components:"
    echo ""
    echo "Subagents:"
    ls -1 "$AGENTS_DIR"/content-*.md | xargs -n 1 basename | sed 's/.md$//' | sed 's/^/  • /'
    echo ""
    echo "Commands:"
    echo "  • /content-pipeline"
    echo ""
}

# Print usage instructions
print_usage() {
    echo ""
    echo -e "${GREEN}Installation Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Open Claude Code"
    echo ""
    echo "2. Verify installation with:"
    echo "   /agents"
    echo ""
    echo "3. Start creating content:"
    echo "   /content-pipeline \"your topic here\""
    echo ""
    echo "4. Or invoke subagents individually:"
    echo "   Use the content-researcher subagent to explore: [topic]"
    echo ""
    echo "Documentation: See README.md for full usage guide"
    echo ""
}

# Main installation flow
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  AI GTM Content System - Installation     ║${NC}"
    echo -e "${BLUE}║  Multi-Subagent LinkedIn Pipeline          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_prerequisites
    setup_directories
    install_agents
    install_command
    verify_installation
    print_usage
}

# Run installation
main
