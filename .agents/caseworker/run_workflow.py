#!/usr/bin/env python3

import os
import sys
import shutil
import argparse
import subprocess
import datetime
import time
import json
from pathlib import Path


def main():
    # 1. Check required environment variables
    required_env_vars = ["JAWAFDEHI_API_BASE_URL", "JAWAFDEHI_API_TOKEN"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Required environment variable(s) not set: {', '.join(missing_vars)}", file=sys.stderr)
        print("Please set the following environment variables:", file=sys.stderr)
        for var in missing_vars:
            print(f"  export {var}=<value>", file=sys.stderr)
        sys.exit(1)
    
    # 2. Check if run from repository root
    if not os.path.isfile("AGENTS.md"):
        print("Error: Must be run from the newnepal-meta repository root (where AGENTS.md exists).", file=sys.stderr)
        sys.exit(1)

    # 3. Parse arguments
    parser = argparse.ArgumentParser(description="Run the casework agent workflow.")
    parser.add_argument("case_number", help="A CIAA case number to process")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the case folder if it already exists")
    parser.add_argument("--preserve", action="store_true", help="Preserve the case folder if it already exists")
    parser.add_argument("--max-iterations", type=int, default=15, help="Maximum number of loop iterations")
    parser.add_argument("--runner", choices=["copilot", "kiro"], default="copilot", help="CLI runner to use (default: copilot)")

    # Simple workaround to support bash-like positional mixed args if they passed manually
    args, unknown = parser.parse_known_args()

    case_number = args.case_number
    overwrite = args.overwrite
    preserve = args.preserve
    max_iterations = args.max_iterations
    runner = args.runner

    if not case_number:
        print("Error: A CIAA case number must be provided.", file=sys.stderr)
        sys.exit(1)

    # 4. Handle folder creation and overwrite
    case_dir = Path("casework") / case_number

    is_existing = case_dir.is_dir()
    if is_existing:
        if preserve:
            print(f"Preserving existing case folder '{case_dir}'...")
        else:
            if not overwrite:
                reply = input(f"Case folder '{case_dir}' already exists. Overwrite? (y/N) ").strip().lower()
                if reply not in ['y', 'yes']:
                    print("Execution cancelled.")
                    sys.exit(1)
            
            print(f"Overwriting '{case_dir}'...")
            shutil.rmtree(case_dir)
            is_existing = False

    if not is_existing or not preserve:
        # 5. Create directories
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "sources" / "raw").mkdir(parents=True, exist_ok=True)
        (case_dir / "sources" / "markdown").mkdir(parents=True, exist_ok=True)

        # 6. Copy internal files and link instructions
        prd_src = Path(".agents/caseworker/etc/prd-template.json")
        if prd_src.exists():
            shutil.copy(prd_src, case_dir / "prd.json")
        else:
            print(f"Warning: {prd_src} not found.", file=sys.stderr)

        instructions_src = Path(".agents/caseworker/instructions").resolve()
        instructions_dest = case_dir.resolve() / "instructions"
        if instructions_dest.exists():
            if instructions_dest.is_symlink() or instructions_dest.is_file():
                instructions_dest.unlink()
            else:
                shutil.rmtree(instructions_dest)
        try:
            os.symlink(instructions_src, instructions_dest)
        except OSError as e:
            print(f"Warning: Failed to create symlink for instructions: {e}", file=sys.stderr)

        # 7. Initialize progress.log
        log_file = case_dir / "progress.log"
        with open(log_file, "w") as f:
            timestamp = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y").strip()
            f.write(f"Case workflow started at {timestamp}\n")

    # 8. Locate runner binary
    if runner == "copilot":
        agent_bin = "/home/codespace/.local/bin/copilot"
        if not os.path.isfile(agent_bin):
            agent_bin = shutil.which("copilot")
        if not agent_bin:
            print("Error: 'copilot' not found. Install GitHub Copilot CLI first.", file=sys.stderr)
            sys.exit(1)
        # MCP config for Jawafdehi and fetch servers (relative to repo root)
        mcp_config = Path(".agents/caseworker/etc/copilot-mcp-config.json")
        if not mcp_config.exists():
            print(f"Warning: MCP config not found at {mcp_config}", file=sys.stderr)
    else:
        agent_bin = shutil.which("kiro-cli")
        if not agent_bin:
            print("Error: 'kiro-cli' not found on PATH.", file=sys.stderr)
            sys.exit(1)
        mcp_config = None

    print(f"Starting agentic workflow runner loop for case {case_number} (runner: {runner})...")

    # 9. Loop runner
    retry_count = 0
    iteration_count = 0
    while iteration_count < max_iterations:
        print("==========================================================")
        
        prd_file = case_dir / "prd.json"
        if prd_file.exists():
            try:
                with open(prd_file, "r") as f:
                    prd_data = json.load(f)
                    if prd_data.get("is_complete", False):
                        print("Workflow marked as complete in prd.json. Exiting loop.")
                        break
            except Exception as e:
                print(f"Warning: Failed to read prd.json: {e}")

        print(f"Invoking {runner} CLI to process task (Iteration {iteration_count + 1}/{max_iterations})...")

        # Construct the command
        if runner == "copilot":
            cmd = [
                agent_bin,
                "--allow-all",
                "--agent", "jawafdehi-caseworker",
            ]
            if mcp_config and mcp_config.exists():
                cmd += ["--additional-mcp-config", f"@{mcp_config}"]
            cmd += ["-p", f"Follow {case_dir}/instructions/INSTRUCTIONS.md"]
        else:
            cmd = [
                agent_bin,
                "chat",
                "--agent", "jawafdehi-caseworker",
                "--no-interactive",
                "--require-mcp-startup",
                f"Follow {case_dir}/instructions/INSTRUCTIONS.md",
            ]

        # Run process
        try:
            result = subprocess.run(cmd)
            exit_code = result.returncode
        except KeyboardInterrupt:
            print("\nWorkflow interrupted by user.")
            break

        if exit_code != 0:
            if exit_code == 130:
                print("\nWorkflow interrupted by user (Exit 130).")
                break
            
            retry_count += 1
            if retry_count > 3:
                print(f"{runner} CLI failed {retry_count} times in a row. Maximum retries exceeded. Aborting.")
                break

            print(f"{runner} CLI exited with code {exit_code}. Retrying in 10 seconds (Attempt {retry_count}/3)...")
            time.sleep(10)
            continue

        retry_count = 0
        iteration_count += 1
        print("Task complete. Waiting before starting the next block...")
        time.sleep(2)
        
        # In Bash script there was a distinct `exit 1` block meant for debugging, 
        # but to keep the workflow loop alive realistically, we won't exit by default on success. 
        # (Commented out in python to match the spirit of the 'while true' loop without the debug exit)
        # sys.exit(1)

    if iteration_count >= max_iterations:
        print(f"Reached maximum iterations ({max_iterations}). Exiting loop.")

    print("Workflow complete.")

if __name__ == "__main__":
    main()
