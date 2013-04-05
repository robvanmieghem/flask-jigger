"""
Renderers are used to serialize a response into specific media types.

They give us a generic way of being able to handle various media types
on the response, such as JSON encoded data or HTML output.


A HTML renderer is also provided that renders the browsable API.

This file is based on the Django REST framework renderers
"""
from __future__ import unicode_literals

import string
import json

from flask import render_template
from util import encoders
from util.breadcrumbs import get_breadcrumbs

from __init__ import VERSION
import status


class BaseRenderer(object):
    """
    All renderers should extend this class, setting the `media_type`
    and `format` attributes, and override the `.render()` method.
    """

    media_type = None
    format = None

    def render(self, data, accepted_media_type=None, renderer_context=None):
        raise NotImplemented('Renderer class requires .render() to be implemented')


class JSONRenderer(BaseRenderer):
    """
    Renderer which serializes to json.
    """

    media_type = 'application/json'
    format = 'json'
    encoder_class = encoders.JSONEncoder

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `obj` into json.
        """
        if data is None:
            return ''

        # If 'indent' is provided in the context, then pretty print the result.
        # E.g. If we're being called by the BrowseableAPIRenderer.
        renderer_context = renderer_context or {}
        indent = renderer_context.get('indent', None)
        request = renderer_context.get('request', None)
        
        if (indent is None) and (request is not None):
            # If the media type looks like 'application/json; indent=4',
            # then pretty print the result.
            indent = request.accept_mimetypes[JSONRenderer.media_type]

        return json.dumps(data, cls=self.encoder_class, indent=indent)


class JSONPRenderer(JSONRenderer):
    """
    Renderer which serializes to json,
    wrapping the json output in a callback function.
    """

    media_type = 'application/javascript'
    format = 'jsonp'
    callback_parameter = 'callback'
    default_callback = 'callback'

    def get_callback(self, renderer_context):
        """
        Determine the name of the callback to wrap around the json output.
        """
        request = renderer_context.get('request', None)
        params = request and request.QUERY_PARAMS or {}
        return params.get(self.callback_parameter, self.default_callback)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders into jsonp, wrapping the json output in a callback function.

        Clients may set the callback function name using a query parameter
        on the URL, for example: ?callback=exampleCallbackName
        """
        renderer_context = renderer_context or {}
        callback = self.get_callback(renderer_context)
        json = super(JSONPRenderer, self).render(data, accepted_media_type,
                                                 renderer_context)
        return "%s(%s);" % (callback, json)


class BrowsableAPIRenderer(BaseRenderer):
    """
    HTML renderer used to self-document the API.
    """
    media_type = 'text/html'
    format = 'api'
    template = 'rest_framework/api.html'

    def get_default_renderer(self, view):
        """
        Return an instance of the first valid renderer.
        (Don't use another documenting renderer.)
        """
        renderers = [renderer for renderer in view.renderer_classes
                     if not issubclass(renderer, BrowsableAPIRenderer)]
        if not renderers:
            return None
        return renderers[0]()

    def get_content(self, renderer, data,
                    accepted_media_type, renderer_context):
        """
        Get the content as if it had been rendered by the default
        non-documenting renderer.
        """
        if not renderer:
            return '[No renderers were found]'

        renderer_context['indent'] = 4
        content = renderer.render(data, accepted_media_type, renderer_context)

        if not all(char in string.printable for char in content):
            return '[%d bytes of binary content]'

        return content

    def show_form_for_method(self, view, method, request, obj):
        """
        Returns True if a form should be shown for this method.
        TODO
        """
        return False



    def get_name(self, view):
        try:
            return view.get_name()
        except AttributeError:
            return view.__function__.__name__

    def get_description(self, view):
        try:
            return view.get_description(html=True)
        except AttributeError:
            return view.__doc__ or ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders *obj* using the :attr:`template` set on the class.

        The context used in the template contains all the information
        needed to self-document the response to this request.
        """
        accepted_media_type = accepted_media_type or ''
        renderer_context = renderer_context or {}

        view = renderer_context['view']
        request = renderer_context['request']
        response = renderer_context['response']
        media_types = [parser.media_type for parser in view.parser_classes]

        renderer = self.get_default_renderer(view)
        content = self.get_content(renderer, data, accepted_media_type, renderer_context)

        name = self.get_name(view)
        description = self.get_description(view)
        breadcrumb_list = get_breadcrumbs(request.path)

        context = {
            'content': content,
            'view': view,
            'request': request,
            'response': response,
            'description': description,
            'name': name,
            'version': VERSION,
            'breadcrumblist': breadcrumb_list,
            'allowed_methods': view.allowed_methods,
            'available_formats': [renderer.format for renderer in view.renderer_classes]
        }

        ret = render_template('show_entries.html', context=context)
        
        # Munge DELETE Response code to allow us to return content
        # (Do this *after* we've rendered the template so that we include
        # the normal deletion response code in the output)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            response.status_code = status.HTTP_200_OK

        return ret
