from flask import request, abort
from flask.globals import current_app
import status
from renderers import JSONRenderer, JSONPRenderer, BrowsableAPIRenderer


default_renderers = [JSONRenderer(), JSONPRenderer(), BrowsableAPIRenderer()]

def api_view(view_function, renderers=default_renderers):
    '''
    If 'renderers' is None, no special rendering will be done, the result of the function will just be passed to Flask to convert it a response.
    '''
    
    def decorator(*args, **kwargs):
        data = view_function(*args, **kwargs)
        
        if renderers is None:
            return data;
        
        #Search the best renderer
        media_type = request.accept_mimetypes.best_match([renderer.media_type for renderer in renderers], None)
        if media_type is None:
            abort(status.HTTP_406_NOT_ACCEPTABLE)
        
        renderer = filter(lambda x:x.media_type == media_type,renderers)[0]
        
        #Render the result of the view function
        rendered_content = renderer.render(data, media_type, 
                                           {'request':request,
                                            'view':view_function})
        
        #Create a matching response
        response = current_app.response_class(
            rendered_content, mimetype=media_type)
        
        return response    
            
    return decorator