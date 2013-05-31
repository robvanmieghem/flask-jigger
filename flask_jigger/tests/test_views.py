import unittest
import mock
import flask
from flask_jigger.views import api_view

class Test_Views(unittest.TestCase):

    def test_api_view(self):
        targetview = mock.MagicMock()
        targetview.return_value = {'testkey':'testvalue'}
        
        renderer = mock.MagicMock()
        renderer.render = mock.MagicMock()
        renderer.render.return_value = 'ALL_OK'
        renderer.media_type = 'application/testmediatype'
        
        app = flask.Flask(__name__)
        app.add_url_rule("/test/<id>", 'test_function', api_view(targetview,[renderer]))
            
        with app.test_request_context('/test/123', headers={'Accept':'application/testmediatype'}):
            response = app.full_dispatch_request()
            self.assertEqual(response.data, 'ALL_OK')
                
        targetview.assert_called_once_with(id='123')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()