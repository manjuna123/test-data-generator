# API Test Data Generator and Robot Framework Test Suite

This project helps you generate test data from OpenAPI specifications and use it in Robot Framework tests to validate your APIs.

## Setup

1. Open this project in VS Code with Dev Containers extension installed
2. Click "Reopen in Container" when prompted
3. Wait for the container to build and initialize

## How to Use

1. Place your OpenAPI specification file in this directory (YAML or JSON format)
2. Run tests using the provided script:

```bash
python run_tests.py --spec your_api_spec.yaml --url https://your-api-url.com
```

## Components

- **api_spec_parser.py**: Parses OpenAPI specifications
- **test_data_generator.py**: Generates test data based on API schemas
- **api_testing_library.py**: Robot Framework library for API testing
- **example_test.robot**: Example Robot Framework test suite

## Creating Custom Tests

1. Create a new `.robot` file based on the example
2. Use the provided keywords:
   - `Load API Specification` - Load your OpenAPI spec
   - `Set Base URL` - Configure the API endpoint
   - `Generate Test Data For Endpoint` - Create test data for a specific endpoint
   - `Make Request` - Send requests to the API
   - Various assertion keywords to validate responses

## Example

```robotframework
*** Settings ***
Library    ApiTestingLibrary

*** Test Cases ***
Test User Creation
    Load API Specification    api_spec.yaml
    Set Base URL    https://api.example.com
    Generate Test Data For Endpoint    /users    POST
    ${response}=    Make Request    POST    /users
    Response Status Code Should Be    201
    Response Should Contain Property    id
```
