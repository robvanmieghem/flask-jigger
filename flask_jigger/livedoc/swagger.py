from flask import request, current_app
import flask_jigger.views
import re

class SwaggerDoc(object):
    
    def _generate_parameter(self, argument, rule):
    
        import werkzeug.routing
        
        if isinstance(rule._converters[argument],werkzeug.routing.FloatConverter):
            datatype = "float"
        else:
            datatype = "string"
        #TODO: more supported types
                
        parameter = {
                    "paramType": "path",
                    "name": argument,
                    #TODO: "description": "blablabla",
                    "dataType": datatype,
                    "required": True,
                    "allowMultiple": False
                   }
        
        return parameter
    
    
    def _description_from_name(self, view_function):
        """
        Translate 'CamelCaseNames' to 'Camel Case Names'.
        Used when generating names from view classes.
        """
        name = view_function.__name__
        camelcase_boundry = '(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))'
        content = re.sub(camelcase_boundry, ' \\1', name).strip()
        return ' '.join(content.split('_')).title()
    
    
    def _generate_apis(self,endpoint):
        apis = []
        
        rules = current_app.url_map._rules_by_endpoint[endpoint]
        view_target = current_app.view_functions[endpoint]
        
        if isinstance(view_target,flask_jigger.views.ApiView):
            view_target = view_target.view_function
        
        view_function_docstring = view_target.__doc__
        view_function_name = self._description_from_name(view_target)

        
        for rule in rules:
            tmp = []
            for is_dynamic, data in rule._trace:
                if is_dynamic:
                    tmp.append('{%s}' % data)
                else:
                    tmp.append(data)
            
            path = u''.join(tmp).lstrip('|')
        
            api = {
                  "path":path,
                  "operations":[]
                  }
            
            parameters = []
            
            for argument in rule.arguments:
                parameters.append(self._generate_parameter(argument, rule))
            
            for method in rule.methods:
                if method in ['GET','PUT', 'POST', 'DELETE']:
                    operation = {
                         "httpMethod":method,
                         "nickname": method + endpoint,
                         "parameters":parameters,
                         "summary": view_function_name,
                         "notes": view_function_docstring,
                         "errorResponses":[]
                         }
            
                    api['operations'].append(operation)
                    
            apis.append(api)
         
        return apis
    
    def generate_resource_description(self,endpoints):
        '''
        Create a swagger description for a list of endpoints
        
        @param endpoints : list of str
            The endpoints as passed to flask that need to be included in the api.
        
        '''
        description = {
                   "apiVersion": "0.2",
                   "swaggerVersion": "1.1",
                   "basePath": request.url_root,
                   "resourcePath": request.path,
                   "apis" : [],
                   "models" : {}
                   }
        for endpoint in endpoints:
            description['apis'].extend(self._generate_apis(endpoint))
        
        return description
    
    def generate_resource_listing(self, endpoints):
        '''
        Create a swagger resource listing for a list of endpoints
        
        @param endpoints : list of str
            The endpoints as passed to flask that need to be included in the resourcelisting.
        
        '''
        resourcelisting = {
            'apiVersion': "0.1",
            'swaggerVersion': "1.1",
            'basePath': request.url,
            'apis': [
                     ]
        }
        
        for endpoint in endpoints:
            resourcelisting['apis'].append({
                                            'path': "/%s.{format}" % endpoint,
                                            'description': ""
                                            })
        
       
        return resourcelisting