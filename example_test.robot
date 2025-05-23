*** Settings ***
Library    ApiTestingLibrary

*** Variables ***
${API_SPEC_FILE}    ${CURDIR}/api_spec.yaml
${BASE_URL}         https://jsonplaceholder.typicode.com

*** Test Cases ***
Test Get Users
    Load API Specification    ${API_SPEC_FILE}
    Set Base URL    ${BASE_URL}
    GenTesterate  Data For Endpoint    /users    GET
    ${response}=    Make Request    GET    /users
    Response Status Code Should Be    200
    Response Should Contain Property    0.id
    Response Should Contain Property    0.name