import requests
import json
import os
from robot.api.deco import keyword
from robot.api import logger
from api_spec_parser import ApiSpecParser
from test_data_generator import TestDataGenerator
from ai_test_data_generator import AiTestDataGenerator

class ApiTestingLibrary:
    """Library for testing APIs based on OpenAPI specifications."""
    
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.last_response = None
        self.test_data = {}
        self.api_parser = None
        self.data_generator = None
        self.ai_generator = None
    
    @keyword
    def load_api_specification(self, spec_file_path):
        """Load and parse the OpenAPI specification file."""
        self.api_parser = ApiSpecParser(spec_file_path)
        self.data_generator = TestDataGenerator(self.api_parser)
        # AI generator will be initialized later when needed
        return f"API specification loaded from {spec_file_path}"
    
    @keyword
    def set_base_url(self, base_url):
        """Set the base URL for API requests."""
        self.base_url = base_url
        return f"Base URL set to {base_url}"
    
    @keyword
    def load_test_data_from_file(self, file_path):
        """Load test data from a JSON file."""
        with open(file_path, 'r') as f:
            self.test_data = json.load(f)
        return f"Test data loaded from {file_path}"
    
    @keyword
    def make_request(self, method, endpoint, data=None, params=None, headers=None):
        """Make an API request with the given method, endpoint, and data."""
        if not self.base_url:
            raise ValueError("Base URL must be set first using 'Set Base URL' keyword")
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Use test data if no specific data is provided
        if data is None and 'request' in self.test_data:
            if isinstance(self.test_data['request'], dict):
                data = self.test_data['request']
        
        # Convert data to JSON string if it's a dictionary
        if isinstance(data, dict):
            data = json.dumps(data)
            headers = headers or {}
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
        
        # Make the request
        logger.info(f"Making {method.upper()} request to {url}")
        if data:
            logger.info(f"Request data: {data}")
        
        self.last_response = self.session.request(
            method=method.upper(),
            url=url,
            data=data,
            params=params,
            headers=headers
        )
        
        try:
            response_json = self.last_response.json()
            logger.info(f"Response ({self.last_response.status_code}): {json.dumps(response_json, indent=2)}")
        except:
            logger.info(f"Response ({self.last_response.status_code}): {self.last_response.text}")
        
        return self.last_response
    
    @keyword
    def response_status_code_should_be(self, expected_status_code):
        """Verify that the response status code matches the expected value."""
        if not self.last_response:
            raise ValueError("No request has been made yet")
        
        actual_status_code = self.last_response.status_code
        expected_status_code = int(expected_status_code)
        
        if actual_status_code != expected_status_code:
            raise AssertionError(f"Expected status code {expected_status_code}, but got {actual_status_code}")
        
        return f"Response status code is {actual_status_code} as expected"
    
    @keyword
    def response_should_contain_property(self, property_path):
        """Verify that the response contains the specified property, supporting list indices."""
        if not self.last_response:
            raise ValueError("No request has been made yet")
        try:
            response_json = self.last_response.json()
        except:
            raise ValueError("Response is not valid JSON")
        # Navigate through nested properties using dot notation, supporting list indices
        properties = property_path.split('.')
        current = response_json
        for prop in properties:
            if isinstance(current, list):
                try:
                    idx = int(prop)
                    current = current[idx]
                except (ValueError, IndexError):
                    raise AssertionError(f"List index '{prop}' not found in response at this level")
            elif isinstance(current, dict) and prop in current:
                current = current[prop]
            else:
                raise AssertionError(f"Property '{property_path}' not found in response")
        return f"Property '{property_path}' found in response"
    
    @keyword
    def response_property_should_equal(self, property_path, expected_value):
        """Verify that a response property equals the expected value."""
        if not self.last_response:
            raise ValueError("No request has been made yet")
        
        try:
            response_json = self.last_response.json()
        except:
            raise ValueError("Response is not valid JSON")
        
        # Navigate through nested properties
        properties = property_path.split('.')
        current = response_json
        
        for prop in properties:
            if isinstance(current, dict) and prop in current:
                current = current[prop]
            else:
                raise AssertionError(f"Property '{property_path}' not found in response")
        
        # Convert expected_value to the same type as the actual value if needed
        if isinstance(current, int) and not isinstance(expected_value, int):
            try:
                expected_value = int(expected_value)
            except:
                pass
        elif isinstance(current, float) and not isinstance(expected_value, float):
            try:
                expected_value = float(expected_value)
            except:
                pass
        
        if current != expected_value:
            raise AssertionError(f"Property '{property_path}' value '{current}' does not match expected '{expected_value}'")
        
        return f"Property '{property_path}' has expected value '{expected_value}'"
    
    @keyword
    def generate_ai_test_data_for_endpoint(self, endpoint_path, method, ai_provider="openai", save_to_file=None):
        """Generate test data for a specific endpoint using AI and optionally save to file.
        
        Args:
            endpoint_path: The path of the endpoint (e.g., /users)
            method: The HTTP method (e.g., GET, POST)
            ai_provider: The AI provider to use ("openai" or "anthropic")
            save_to_file: Optional path to save the generated test data
            
        Returns:
            The generated test data in JSON format
        """
        if not self.ai_generator:
            # Create a new AI generator with the specified provider
            if not self.api_parser:
                raise ValueError("API specification must be loaded first using 'Load API Specification' keyword")
            self.ai_generator = AiTestDataGenerator(self.api_parser, provider=ai_provider)
        elif self.ai_generator.provider != ai_provider.lower():
            # If provider changed, create a new generator
            self.ai_generator = AiTestDataGenerator(self.api_parser, provider=ai_provider)
        
        # Generate test data using AI
        logger.info(f"Generating AI test data for {method.upper()} {endpoint_path} using {ai_provider}")
        test_data = self.ai_generator.generate_test_data_for_endpoint(endpoint_path, method)
        self.test_data = test_data
        
        if save_to_file:
            self.ai_generator.save_test_data_to_file(test_data, save_to_file)
            logger.info(f"AI-generated test data saved to {save_to_file}")
        
        return json.dumps(test_data, indent=2)
