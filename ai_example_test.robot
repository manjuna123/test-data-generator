*** Settings ***
Library    ApiTestingLibrary

*** Variables ***
${API_SPEC_FILE}    ${CURDIR}/api_spec.yaml
${BASE_URL}         https://jsonplaceholder.typicode.com

*** Test Cases ***
Test With AI Generated Data
    Load API Specification    ${API_SPEC_FILE}
    Set Base URL    ${BASE_URL}
    ${data}=    Generate AI Test Data For Endpoint    /users    POST    ai_provider=anthropic
    Log    ${data}
    ${response}=    Make Request    POST    /users
    Response Status Code Should Be    201
    Response Should Contain Property    id
