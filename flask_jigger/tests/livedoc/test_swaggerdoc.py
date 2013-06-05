import unittest
import mock
import flask
from flask_jigger.views import api_view
import json


class Test_SwaggerDoc(unittest.TestCase):


    def setUp(self):
        self.targetview = mock.MagicMock()
        self.targetview.__name__ = 'test_it'
        self.targetview.return_value = {'testkey':'testvalue'}
        
        self.swaggerview = mock.MagicMock()
        
        self.app = flask.Flask(__name__)
        self.app.add_url_rule("/swagger", 'swagger', api_view(self.swaggerview))
        
    def tearDown(self):
        pass

    def testGenerateApi(self):
        self.app.add_url_rule("/test/<float:id>", 'test_function', api_view(self.targetview),methods=['GET'])
        
        def generateEndpointDoc():
            from flask_jigger.livedoc import swagger
            return swagger.SwaggerDoc().generate_resource_description(['test_function'])
        
        self.swaggerview.side_effect = generateEndpointDoc
        
        with self.app.test_request_context('/swagger', headers={'Accept':'application/json'}):
            response = self.app.full_dispatch_request()
            swaggerdescription = json.loads(response.data)

        self.assertEqual(swaggerdescription['resourcePath'],'/swagger')
        self.assertEqual(swaggerdescription['apis'][0]['path'], '/test/{id}')
        
    def testGenerateApi_Operation(self):
        self.targetview.__doc__ = 'DocDescription'
        
        self.app.add_url_rule("/test/<float:id>", 'test_function', api_view(self.targetview),methods=['GET'])
        
        def generateEndpointDoc():
            from flask_jigger.livedoc import swagger
            return swagger.SwaggerDoc().generate_resource_description(['test_function'])
        
        self.swaggerview.side_effect = generateEndpointDoc
        
        with self.app.test_request_context('/swagger', headers={'Accept':'application/json'}):
            response = self.app.full_dispatch_request()
            swaggerdescription = json.loads(response.data)

        operation = swaggerdescription['apis'][0]['operations'][0]
        self.assertEqual(operation['httpMethod'], 'GET')
        self.assertEqual(operation['notes'], "DocDescription")
        self.assertEqual(operation['summary'],'Test It')
        
        parameter = operation['parameters'][0]
        self.assertEqual(parameter['dataType'], 'float')
        self.assertEqual(parameter['name'], 'id')
        self.assertEqual(parameter['paramType'], 'path')
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()