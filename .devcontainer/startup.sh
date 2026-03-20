#!/bin/bash

set -euo pipefail

# Install uv 
pipx install uv poetry

# Install bun
curl -fsSL https://bun.com/install | bash
