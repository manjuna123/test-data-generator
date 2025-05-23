*** Settings ***
Library    ApiTestingLibrary
Library    OperatingSystem
Library    Collections

*** Variables ***
${API_SPEC_FILE}    ${CURDIR}/api_spec.yaml
${BASE_URL}         http://api.example.com
${TEST_DATA_FILE}   ${CURDIR}/test_data.json

*** Test Cases ***
Test API Endpoints Using Generated Data
    Load API Specification    ${API_SPEC_FILE}
    Set Base URL    ${BASE_URL}
    
    # Example for a GET endpoint
    Generate Test Data For Endpoint    /users/{id}    GET    ${TEST_DATA_FILE}
    ${user_id}=    Set Variable    123
    ${response}=    Make Request    GET    /users/${user_id}
    Response Status Code Should Be    200
    Response Should Contain Property    id
    Response Should Contain Property    name
    
    # Example for a POST endpoint
    Generate Test Data For Endpoint    /users    POST    ${TEST_DATA_FILE}
    ${response}=    Make Request    POST    /users
    Response Status Code Should Be    201
    Response Should Contain Property    id
    
    # Example with custom data
    ${custom_data}=    Create Dictionary    name=Test User    email=test@example.com
    ${response}=    Make Request    POST    /users    data=${custom_data}
    Response Status Code Should Be    201
    Response Property Should Equal    name    Test User

*** Keywords ***
Cleanup Test Data
    [Documentation]    Clean up any test data that was created
    # Add cleanup steps here if needed
