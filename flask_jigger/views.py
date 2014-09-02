from flask import request, abort, current_app
import status
from werkzeug import BaseResponse
from renderers import JSONRenderer, JSONPRenderer, BrowsableAPIRenderer


default_renderers = [JSONRenderer(), JSONPRenderer(), BrowsableAPIRenderer()]


class ApiView():
    '''
    Class for wrapping view_functions, use the api_view decorator to generate instances
    '''
    
    def __init__(self, view_function, renderers):
        self.renderers = renderers
        self.view_function = view_function
        if (hasattr(view_function,'__name__')):
            self.__name__ = view_function.__name__
         
    def __call__(self, *args, **kwargs):
        data = self.view_function(*args, **kwargs)
        
        if self.renderers is None:
            return data;
        
        #Search the best renderer
        media_type = request.accept_mimetypes.best_match([renderer.media_type for renderer in self.renderers], None)
        if media_type is None:
            abort(status.HTTP_406_NOT_ACCEPTABLE)
        
        renderer = filter(lambda x:x.media_type == media_type,self.renderers)[0]
        
        #preliminary response class to pass to the renderer
        beta_response = BaseResponse()
        
        #Render the result of the view function
        rendered_content = renderer.render(data, media_type, 
                                           {'request':request,
                                            'response':beta_response,
                                            'view':self.view_function,
                                            'renderers':self.renderers})
        
        #Create a matching response
        response = current_app.response_class(
            rendered_content, mimetype=media_type)
        
        return response    

def api_view(view_function, renderers=default_renderers):
    '''
    If 'renderers' is None, no special rendering will be done, the result of the function will just be passed to Flask to convert it a response.
    '''
    
    return ApiView(view_function,renderers)