from __future__ import unicode_literals
from flask import request, abort
import views, status

def _accept_mimetype_replacer(view_function,mapping):
    
    def force_mimetype(*args, **kwargs):
        format = kwargs.pop('jigger_mimetype_format')
        
        if format not in mapping:
            abort(status.HTTP_406_NOT_ACCEPTABLE)
        
        import werkzeug.datastructures
        accept = werkzeug.datastructures.MIMEAccept([(mapping[format],1)])
        request.accept_mimetypes = accept
        
        return view_function(*args, **kwargs)
    
    return force_mimetype

def format_suffix_url_rules(application, mapping={'json':'application/json', 'jsonp':'application/jsonp'}):
    """
    Supplement existing url_rules with corresponding rules that also
    include a '.format' suffix.
    
    While handling a request, the request.accept_mimetypes will be replaced to only accept the mimetype requested in the url  
    """
    for (endpoint, view_function) in [item for item in application.view_functions.items()]:
        if (view_function.__module__ == views.api_view.__module__) :
            for rule in [rule for rule in application.url_map._rules_by_endpoint[endpoint]]:
                application.add_url_rule(rule.rule + '.<jigger_mimetype_format>',endpoint + '.<jigger_mimetype_format>', _accept_mimetype_replacer(view_function,mapping))
