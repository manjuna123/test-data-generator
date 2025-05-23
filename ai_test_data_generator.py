"""
AI-based test data generator for OpenAPI specifications.
Leverages LLMs to generate realistic test data.
"""

import os
import json
import logging
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class AiTestDataGenerator:
    """Generate test data using AI models based on OpenAPI specifications."""
    
    def __init__(self, api_parser, provider="openai"):
        """
        Initialize the AI test data generator.
        
        Args:
            api_parser: An instance of ApiSpecParser that contains the OpenAPI spec
            provider: The AI provider to use ("openai" or "anthropic")
        """
        self.api_parser = api_parser
        self.provider = provider.lower()
        self.schemas = api_parser.get_schemas()
        
        # Initialize AI clients
        if self.provider == "openai":
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                logging.warning("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                logging.warning("ANTHROPIC_API_KEY not found in environment variables")
            self.client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}. Use 'openai' or 'anthropic'")
    
    def _generate_from_ai(self, prompt):
        """Generate test data using the selected AI model."""
        if self.provider == "openai":
            return self._generate_from_openai(prompt)
        elif self.provider == "anthropic":
            return self._generate_from_anthropic(prompt)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    def _generate_from_openai(self, prompt):
        """Generate test data using OpenAI."""
        if not self.api_key:
            # Fail the test case instead of generating mock data
            raise ValueError("No OpenAI API key provided. Cannot generate test data.")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # or another model as needed
                messages=[
                    {"role": "system", "content": "You are a helpful API test data generator that creates realistic test data based on OpenAPI schemas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            # Propagate the error instead of returning empty JSON
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def _generate_from_anthropic(self, prompt):
        """Generate test data using Anthropic."""
        if not self.api_key:
            # Fail the test case instead of generating mock data
            raise ValueError("No Anthropic API key provided. Cannot generate test data.")
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use a model that should exist
                max_tokens=2000,
                temperature=0.7,
                system="You are a helpful API test data generator that creates realistic test data based on OpenAPI schemas. You must only return valid JSON without any explanation.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = response.content[0].text
            logging.debug(f"Raw Anthropic response: {response_text}")
            return response_text
        except Exception as e:
            logging.error(f"Anthropic API error: {str(e)}")
            # Propagate the error instead of returning empty JSON
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    def generate_test_data_for_endpoint(self, endpoint_path, method):
        """
        Generate test data for a specific endpoint using AI.
        
        Args:
            endpoint_path: The path of the endpoint (e.g., /users)
            method: The HTTP method (e.g., GET, POST)
            
        Returns:
            A dictionary with request and response data
            
        Raises:
            ValueError: If endpoint is not found or API key is missing
            RuntimeError: If AI provider returns an error
        """
        endpoints = self.api_parser.get_endpoints()
        
        # Find the endpoint in the OpenAPI spec
        endpoint_data = None
        for endpoint in endpoints:
            if endpoint['path'] == endpoint_path and endpoint['method'] == method.upper():
                endpoint_data = endpoint
                break
        
        if not endpoint_data:
            raise ValueError(f"Endpoint not found: {method.upper()} {endpoint_path}")
        
        # Create a prompt for the AI model with the endpoint details
        prompt = self._create_prompt(endpoint_data)
        
        # Generate test data using the AI model - will raise errors if API key is missing or AI fails
        ai_response = self._generate_from_ai(prompt)
        
        try:
            # Parse the JSON response from the AI
            parsed_data = json.loads(ai_response)
            
            # Make sure the response contains request and response data
            if 'request' not in parsed_data:
                parsed_data['request'] = {}
            if 'response' not in parsed_data:
                parsed_data['response'] = {}
            
            return parsed_data
        except json.JSONDecodeError:
            logging.error(f"Failed to parse AI response as JSON: {ai_response}")
            logging.error("AI response might contain formatting that's not valid JSON. Attempting to clean...")
            
            # Try to clean the response by removing extra whitespace and newlines
            cleaned_response = ai_response.strip()
            
            # If it looks like the AI returned text wrapped in ``` (code blocks), try to extract it
            if cleaned_response.startswith("```json") and cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[7:-3].strip()
            elif cleaned_response.startswith("```") and cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[3:-3].strip()
                
            try:
                parsed_data = json.loads(cleaned_response)
                if 'request' not in parsed_data:
                    parsed_data['request'] = {}
                if 'response' not in parsed_data:
                    parsed_data['response'] = {}
                return parsed_data
            except json.JSONDecodeError:
                # Fail the test case instead of using mock data
                raise RuntimeError("Failed to parse AI response as JSON, even after cleaning.")
    
    def _create_prompt(self, endpoint_data):
        """Create a prompt for the AI model based on the endpoint data."""
        endpoint_path = endpoint_data['path']
        method = endpoint_data['method']
        
        # Extract schema information
        request_schema = {}
        if 'requestBody' in endpoint_data and endpoint_data['requestBody']:
            content = endpoint_data['requestBody'].get('content', {})
            if 'application/json' in content:
                request_schema = content['application/json'].get('schema', {})
        
        response_schema = {}
        if '200' in endpoint_data.get('responses', {}):
            response_def = endpoint_data['responses']['200']
            if 'content' in response_def and 'application/json' in response_def['content']:
                response_schema = response_def['content']['application/json'].get('schema', {})
        
        # Format schemas as JSON strings
        request_schema_str = json.dumps(request_schema, indent=2)
        response_schema_str = json.dumps(response_schema, indent=2)
        
        # Create the prompt
        prompt = f"""Generate realistic test data for the following API endpoint:

Endpoint: {endpoint_path}
Method: {method}

Request Schema:
{request_schema_str}

Response Schema:
{response_schema_str}

Please create JSON test data with 'request' and 'response' properties that match these schemas.
The data should be realistic and contextually appropriate for this endpoint.
Only return valid JSON without any explanation or surrounding text.
Format:
{{
  "request": {{...}},
  "response": {{...}}
}}
"""
        return prompt
    
    def save_test_data_to_file(self, test_data, file_path):
        """Save generated test data to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(test_data, f, indent=2)
