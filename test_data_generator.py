import random
import string
import datetime
import json
from faker import Faker

fake = Faker()

class TestDataGenerator:
    def __init__(self, api_parser):
        self.api_parser = api_parser
        self.schemas = api_parser.get_schemas()
    
    def generate_test_data_for_endpoint(self, endpoint_path, method):
        """Generate test data for a specific endpoint."""
        endpoints = self.api_parser.get_endpoints()
        
        for endpoint in endpoints:
            if endpoint['path'] == endpoint_path and endpoint['method'] == method.upper():
                # Generate request data
                request_data = self._generate_request_data(endpoint)
                
                # Generate expected response data
                response_data = self._generate_response_data(endpoint)
                
                return {
                    'request': request_data,
                    'response': response_data
                }
        
        raise ValueError(f"Endpoint not found: {method.upper()} {endpoint_path}")
    
    def _generate_request_data(self, endpoint):
        """Generate request data based on endpoint definition."""
        # Handle request body if present
        if 'requestBody' in endpoint and endpoint['requestBody']:
            content = endpoint['requestBody'].get('content', {})
            
            # Try application/json first
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                return self._generate_from_schema(schema)
            
            # Try other content types if json not available
            for content_type, content_schema in content.items():
                schema = content_schema.get('schema', {})
                return self._generate_from_schema(schema)
        
        # Generate data for parameters
        params_data = {}
        for param in endpoint.get('parameters', []):
            if param['in'] in ['query', 'path', 'header']:
                params_data[param['name']] = self._generate_param_value(param)
        
        return params_data
    
    def _generate_response_data(self, endpoint):
        """Generate expected response data."""
        responses = endpoint.get('responses', {})
        
        # First try 200 response
        if '200' in responses:
            return self._generate_response_for_code(responses['200'])
        
        # Then try 201 (for creation endpoints)
        if '201' in responses:
            return self._generate_response_for_code(responses['201'])
        
        # If no success responses defined, return empty dict
        return {}
    
    def _generate_response_for_code(self, response_def):
        """Generate response data for a specific response code."""
        if 'content' in response_def:
            content = response_def['content']
            
            # Try application/json first
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                return self._generate_from_schema(schema)
        
        return {}
    
    def _generate_from_schema(self, schema):
        """Generate data based on schema definition."""
        if not schema:
            return {}
            
        schema_type = schema.get('type', 'object')
        
        # Handle reference
        if '$ref' in schema:
            ref_path = schema['$ref']
            if ref_path.startswith('#/components/schemas/'):
                schema_name = ref_path.split('/')[-1]
                if schema_name in self.schemas:
                    return self._generate_from_schema(self.schemas[schema_name])
            return {}
        
        # Handle different types
        if schema_type == 'object':
            return self._generate_object(schema)
        elif schema_type == 'array':
            return self._generate_array(schema)
        elif schema_type == 'string':
            return self._generate_string(schema)
        elif schema_type == 'integer':
            return self._generate_integer(schema)
        elif schema_type == 'number':
            return self._generate_number(schema)
        elif schema_type == 'boolean':
            return random.choice([True, False])
        
        return None
    
    def _generate_object(self, schema):
        """Generate an object based on schema."""
        result = {}
        
        if 'properties' not in schema:
            return {}
            
        for prop_name, prop_schema in schema.get('properties', {}).items():
            # Skip if this property is not required and we decide to omit it
            required_props = schema.get('required', [])
            if prop_name not in required_props and random.random() > 0.8:
                continue
                
            result[prop_name] = self._generate_from_schema(prop_schema)
            
        return result
    
    def _generate_array(self, schema):
        """Generate an array based on schema."""
        items_schema = schema.get('items', {})
        min_items = schema.get('minItems', 1)
        max_items = schema.get('maxItems', 3)
        
        num_items = random.randint(min_items, max_items)
        return [self._generate_from_schema(items_schema) for _ in range(num_items)]
    
    def _generate_string(self, schema):
        """Generate a string based on schema."""
        format_type = schema.get('format', '')
        
        if format_type == 'date-time':
            return fake.iso8601()
        elif format_type == 'date':
            return fake.date_this_decade().isoformat()
        elif format_type == 'email':
            return fake.email()
        elif format_type == 'uuid':
            return fake.uuid4()
        elif format_type == 'uri':
            return fake.uri()
        elif format_type == 'password':
            return fake.password()
        elif 'enum' in schema:
            return random.choice(schema['enum'])
        
        # Generate a random string
        min_length = schema.get('minLength', 5)
        max_length = schema.get('maxLength', 10)
        length = random.randint(min_length, max_length)
        
        if 'pattern' in schema:
            # For complex patterns, just use faker to generate something reasonable
            return fake.text(max_nb_chars=length)
        
        return fake.text(max_nb_chars=length)
    
    def _generate_integer(self, schema):
        """Generate an integer based on schema."""
        minimum = schema.get('minimum', 0)
        maximum = schema.get('maximum', 1000)
        
        return random.randint(minimum, maximum)
    
    def _generate_number(self, schema):
        """Generate a number based on schema."""
        minimum = schema.get('minimum', 0.0)
        maximum = schema.get('maximum', 1000.0)
        
        return round(random.uniform(minimum, maximum), 2)
    
    def _generate_param_value(self, param):
        """Generate a value for a parameter."""
        schema = param.get('schema', {})
        return self._generate_from_schema(schema)
    
    def save_test_data_to_file(self, test_data, file_path):
        """Save generated test data to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(test_data, f, indent=2)
