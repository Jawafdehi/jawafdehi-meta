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
    # 1. Check if run from repository root
    if not os.path.isfile("AGENTS.md"):
        print("Error: Must be run from the newnepal-meta repository root (where AGENTS.md exists).", file=sys.stderr)
        sys.exit(1)

    # 2. Parse arguments
    parser = argparse.ArgumentParser(description="Run the casework agent workflow.")
    parser.add_argument("case_number", help="A CIAA case number to process")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the case folder if it already exists")
    parser.add_argument("--preserve", action="store_true", help="Preserve the case folder if it already exists")
    parser.add_argument("--max-iterations", type=int, default=15, help="Maximum number of loop iterations")
    
    # Simple workaround to support bash-like positional mixed args if they passed manually
    args, unknown = parser.parse_known_args()

    case_number = args.case_number
    overwrite = args.overwrite
    preserve = args.preserve
    max_iterations = args.max_iterations

    if not case_number:
        print("Error: A CIAA case number must be provided.", file=sys.stderr)
        sys.exit(1)

    # 3. Handle folder creation and overwrite
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
        # 4. Create directories
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "sources" / "raw").mkdir(parents=True, exist_ok=True)
        (case_dir / "sources" / "markdown").mkdir(parents=True, exist_ok=True)

        # 5. Copy internal files and link instructions
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

        # 6. Initialize progress.log
        log_file = case_dir / "progress.log"
        with open(log_file, "w") as f:
            timestamp = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y").strip()
            f.write(f"Case workflow started at {timestamp}\n")

    print(f"Starting agentic workflow runner loop for case {case_number}...")

    # 7. Loop runner
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

        print(f"Invoking kiro-cli to process task (Iteration {iteration_count + 1}/{max_iterations})...")

        # Construct the command
        cmd = [
            "kiro-cli",
            "chat",
            "--agent",
            "jawafdehi-caseworker",
            "--no-interactive",
            "--require-mcp-startup",
            f"Follow {case_dir}/instructions/INSTRUCTIONS.md"
        ]

        # Run process
        try:
            result = subprocess.run(cmd, env=os.environ)
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
                print(f"Kiro CLI failed {retry_count} times in a row. Maximum retries exceeded. Aborting.")
                break

            print(f"Kiro CLI exited with code {exit_code}. Retrying in 10 seconds (Attempt {retry_count}/3)...")
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
