import yaml
import json
import os
from openapi_spec_validator import validate_spec

class ApiSpecParser:
    def __init__(self, spec_file_path):
        self.spec_file_path = spec_file_path
        self.spec_data = self._load_spec()
        self._validate_spec()
        
    def _load_spec(self):
        """Load API specification from file."""
        _, ext = os.path.splitext(self.spec_file_path)
        
        with open(self.spec_file_path, 'r') as file:
            if ext.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(file)
            elif ext.lower() == '.json':
                return json.load(file)
            else:
                raise ValueError(f"Unsupported file format: {ext}. Use YAML or JSON.")
    
    def _validate_spec(self):
        """Validate that the loaded spec conforms to OpenAPI standard."""
        validate_spec(self.spec_data)
        
    def get_endpoints(self):
        """Extract all endpoints from the API spec."""
        endpoints = []
        
        for path, path_item in self.spec_data.get('paths', {}).items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoints.append({
                        'path': path,
                        'method': method.upper(),
                        'operation_id': operation.get('operationId'),
                        'summary': operation.get('summary', ''),
                        'parameters': operation.get('parameters', []),
                        'request_body': operation.get('requestBody', {}),
                        'responses': operation.get('responses', {})
                    })
        
        return endpoints
    
    def get_schemas(self):
        """Extract all schemas from the API spec."""
        components = self.spec_data.get('components', {})
        return components.get('schemas', {})
