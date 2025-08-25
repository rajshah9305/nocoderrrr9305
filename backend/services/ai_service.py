import os
import requests
import json
import time
from datetime import datetime

class AIService:
    def __init__(self):
        self.cerebras_api_key = os.getenv('CEREBRAS_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    
    def analyze_requirements(self, description, requirements=None):
        prompt = f"""
You are a senior requirements analyst. Analyze the following app description and create comprehensive technical specifications.

APP DESCRIPTION:
{description}

ADDITIONAL REQUIREMENTS:
{json.dumps(requirements, indent=2) if requirements else 'None specified'}

Please provide a detailed analysis in the following JSON format:

{{
  "overview": {{
    "app_name": "Suggested app name",
    "category": "App category (e.g., productivity, social, ecommerce)",
    "target_audience": "Primary target users",
    "core_value": "Main value proposition"
  }},
  "functional_requirements": [
    {{
      "id": "FR001",
      "title": "Feature title",
      "description": "Detailed feature description",
      "priority": "high|medium|low",
      "complexity": "low|medium|high"
    }}
  ],
  "technical_requirements": {{
    "frontend": {{
      "framework": "React",
      "libraries": ["List of required libraries"],
      "features": ["PWA", "Responsive Design", "etc."]
    }},
    "backend": {{
      "language": "Node.js",
      "database": "PostgreSQL",
      "apis": ["List of required APIs"],
      "services": ["List of required services"]
    }},
    "infrastructure": {{
      "hosting": "Vercel",
      "deployment": "Continuous",
      "scaling": "Auto"
    }}
  }},
  "user_stories": [
    {{
      "id": "US001",
      "role": "User role",
      "goal": "What they want to achieve",
      "benefit": "Why they want it",
      "acceptance_criteria": ["List of acceptance criteria"]
    }}
  ],
  "estimated_complexity": "low|medium|high",
  "estimated_timeframe": "Development timeframe estimate"
}}
        """
        
        try:
            result = self._call_ai_service(prompt, "requirements_analysis")
            return self._parse_json_response(result, self._get_default_requirements())
        except Exception as e:
            return self._get_default_requirements(error=str(e))
    
    def design_architecture(self, description, specifications=None):
        prompt = f"""
You are a system architect. Design a comprehensive system architecture for the following application.

APP DESCRIPTION:
{description}

SPECIFICATIONS:
{json.dumps(specifications, indent=2) if specifications else 'None provided'}

Please provide a detailed architecture design in JSON format:

{{
  "system_overview": {{
    "architecture_pattern": "MVC|Microservices|Serverless",
    "scalability_approach": "Horizontal|Vertical|Auto-scaling",
    "security_model": "JWT|OAuth2|Session-based"
  }},
  "frontend_architecture": {{
    "framework": "React",
    "state_management": "Redux|Context|Zustand",
    "routing": "React Router",
    "styling": "Tailwind CSS|Styled Components",
    "build_tool": "Vite|Webpack"
  }},
  "backend_architecture": {{
    "framework": "Express.js|Fastify|NestJS",
    "database": {{
      "primary": "PostgreSQL|MongoDB|MySQL",
      "caching": "Redis|Memcached",
      "search": "Elasticsearch|Algolia"
    }},
    "api_design": "REST|GraphQL|tRPC",
    "authentication": "JWT|Passport|Auth0"
  }},
  "deployment_architecture": {{
    "frontend_hosting": "Vercel|Netlify|AWS S3",
    "backend_hosting": "Railway|Heroku|AWS ECS",
    "database_hosting": "Supabase|PlanetScale|AWS RDS",
    "cdn": "Cloudflare|AWS CloudFront",
    "monitoring": "Sentry|DataDog|New Relic"
  }}
}}
        """
        
        try:
            result = self._call_ai_service(prompt, "architecture_design")
            return self._parse_json_response(result, self._get_default_architecture())
        except Exception as e:
            return self._get_default_architecture(error=str(e))
    
    def create_design(self, description, specifications=None):
        prompt = f"""
You are a UI/UX designer. Create comprehensive design specifications for the following application.

APP DESCRIPTION:
{description}

SPECIFICATIONS:
{json.dumps(specifications, indent=2) if specifications else 'None provided'}

Please provide detailed design specifications in JSON format:

{{
  "design_system": {{
    "color_palette": {{
      "primary": "#3B82F6",
      "secondary": "#10B981",
      "accent": "#F59E0B",
      "neutral": "#6B7280",
      "background": "#F9FAFB",
      "text": "#111827"
    }},
    "typography": {{
      "font_family": "Inter, system-ui, sans-serif",
      "headings": "font-bold",
      "body": "font-normal"
    }}
  }},
  "layout_structure": {{
    "header": {{
      "height": "4rem",
      "components": ["Logo", "Navigation", "User Menu"],
      "sticky": true
    }},
    "main_content": {{
      "max_width": "1200px",
      "padding": "2rem",
      "responsive": true
    }}
  }},
  "component_designs": [
    {{
      "name": "Button",
      "variants": ["primary", "secondary", "outline", "ghost"],
      "sizes": ["sm", "md", "lg"],
      "states": ["default", "hover", "active", "disabled"]
    }}
  ]
}}
        """
        
        try:
            result = self._call_ai_service(prompt, "ui_design")
            return self._parse_json_response(result, self._get_default_design())
        except Exception as e:
            return self._get_default_design(error=str(e))
    
    def generate_frontend_code(self, description, previous_results):
        prompt = f"""
Generate React component code for the following application.

APP DESCRIPTION:
{description}

PREVIOUS RESULTS:
{json.dumps(previous_results, indent=2)}

Generate a complete React application structure with components and styling.
        """
        
        try:
            result = self._call_ai_service(prompt, "frontend_code")
            return self._parse_json_response(result, self._get_default_frontend_code())
        except Exception as e:
            return self._get_default_frontend_code(error=str(e))
    
    def generate_backend_code(self, description, previous_results):
        prompt = f"""
Generate Node.js/Express API code for the following application.

APP DESCRIPTION:
{description}

PREVIOUS RESULTS:
{json.dumps(previous_results, indent=2)}

Generate a complete backend API with routes, models, and middleware.
        """
        
        try:
            result = self._call_ai_service(prompt, "backend_code")
            return self._parse_json_response(result, self._get_default_backend_code())
        except Exception as e:
            return self._get_default_backend_code(error=str(e))
    
    def create_deployment_config(self, description, previous_results):
        return {
            "platform": "Vercel",
            "build_command": "npm run build",
            "output_directory": "dist",
            "environment_variables": [
                "NODE_ENV=production",
                "API_URL=https://api.example.com"
            ],
            "domains": ["app.example.com"],
            "ssl": True,
            "cdn": True,
            "monitoring": {
                "enabled": True,
                "alerts": ["error_rate", "response_time"]
            }
        }
    
    def _call_ai_service(self, prompt, task_type):
        if self.cerebras_api_key:
            try:
                return self._call_cerebras(prompt)
            except Exception as e:
                print(f"Cerebras API failed: {e}")
        
        if self.openai_api_key:
            try:
                return self._call_openai(prompt)
            except Exception as e:
                print(f"OpenAI API failed: {e}")
        
        return self._get_mock_response(task_type)
    
    def _call_cerebras(self, prompt):
        # Mock implementation for Cerebras
        return self._get_mock_response("cerebras_response")
    
    def _call_openai(self, prompt):
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 4000,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return self._get_mock_response("openai_error")
        
        except Exception as e:
            return self._get_mock_response("openai_error")
    
    def _parse_json_response(self, response, default_value):
        try:
            if isinstance(response, str):
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response[start:end]
                    return json.loads(json_str)
            
            return response if isinstance(response, dict) else default_value
        except Exception as e:
            print(f"Failed to parse JSON response: {e}")
            return default_value
    
    def _get_mock_response(self, task_type):
        return f"Mock {task_type} response - AI service integration in progress"
    
    def _get_default_requirements(self, error=None):
        return {
            "overview": {
                "app_name": "Generated App",
                "category": "web-application",
                "target_audience": "General users",
                "core_value": "Provides useful functionality"
            },
            "functional_requirements": [
                {
                    "id": "FR001",
                    "title": "User Interface",
                    "description": "Modern, responsive user interface",
                    "priority": "high",
                    "complexity": "medium"
                }
            ],
            "technical_requirements": {
                "frontend": {
                    "framework": "React",
                    "libraries": ["React Router", "Tailwind CSS"],
                    "features": ["Responsive Design", "Modern UI"]
                },
                "backend": {
                    "language": "Node.js",
                    "database": "PostgreSQL",
                    "apis": ["REST API"],
                    "services": ["Authentication"]
                }
            },
            "estimated_complexity": "medium",
            "estimated_timeframe": "2-4 weeks",
            "error": error
        }
    
    def _get_default_architecture(self, error=None):
        return {
            "system_overview": {
                "architecture_pattern": "MVC",
                "scalability_approach": "Auto-scaling",
                "security_model": "JWT"
            },
            "frontend_architecture": {
                "framework": "React",
                "state_management": "Context",
                "routing": "React Router",
                "styling": "Tailwind CSS",
                "build_tool": "Vite"
            },
            "backend_architecture": {
                "framework": "Express.js",
                "database": {
                    "primary": "PostgreSQL",
                    "caching": "Redis"
                },
                "api_design": "REST",
                "authentication": "JWT"
            },
            "error": error
        }
    
    def _get_default_design(self, error=None):
        return {
            "design_system": {
                "color_palette": {
                    "primary": "#3B82F6",
                    "secondary": "#10B981",
                    "accent": "#F59E0B",
                    "neutral": "#6B7280",
                    "background": "#F9FAFB",
                    "text": "#111827"
                },
                "typography": {
                    "font_family": "Inter, system-ui, sans-serif",
                    "headings": "font-bold",
                    "body": "font-normal"
                }
            },
            "error": error
        }
    
    def _get_default_frontend_code(self, error=None):
        return {
            "app_component": "// React App component code",
            "components": {
                "Header": "// Header component",
                "Dashboard": "// Dashboard component"
            },
            "error": error
        }
    
    def _get_default_backend_code(self, error=None):
        return {
            "server_js": "// Express server code",
            "routes": {
                "auth": "// Auth routes",
                "api": "// API routes"
            },
            "error": error
        }