#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Run API tests with Robot Framework')
    parser.add_argument('--spec', required=True, help='Path to the OpenAPI specification file')
    parser.add_argument('--url', required=True, help='Base URL of the API to test')
    parser.add_argument('--output', default='results', help='Directory to store test results')
    
    args = parser.parse_args()
    
    # Check if spec file exists
    if not os.path.isfile(args.spec):
        print(f"Error: API specification file not found: {args.spec}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Run Robot Framework tests
    command = [
        "robot",
        f"--variable", f"API_SPEC_FILE:{args.spec}",
        f"--variable", f"BASE_URL:{args.url}",
        f"--outputdir", args.output,
        "example_test.robot"
    ]
    
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command)

if __name__ == "__main__":
    main()
