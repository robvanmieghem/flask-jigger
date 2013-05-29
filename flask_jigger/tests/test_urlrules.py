import unittest
import mock
from flask_jigger.urlrules import format_suffix_url_rules
from flask_jigger.views import api_view
import flask


class TestUrlRules(unittest.TestCase):


    def test_format_suffix_url_rules(self):
        with mock.MagicMock() as targetview:
            
            def check_request_effect(*args,**kwargs):
                #No arguments passed
                self.assertEqual(len(kwargs),0)
                #Should only accept json, nothing else
                self.assertTrue(flask.request.accept_mimetypes.accept_json)
                self.assertFalse(flask.request.accept_mimetypes.accept_html)
            
            targetview.side_effect = check_request_effect
             
            app = flask.Flask(__name__)
            app.add_url_rule("/test", 'test_function', api_view(targetview))
            
            format_suffix_url_rules(app)
            
            with app.test_request_context('/test.json'):
                app.full_dispatch_request()
                
            targetview.assert_called_once_with()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_url']
    unittest.main()