from flask import url_for

def hyperlink_ids(documents, endpoint, id_parameter_name , **values):
    """
    Replace mongo "_id" objectid fields with a 'uri' representing this object
    parameter endpoint: the flask endpoint the url should point to
    parameter id_parameter_name: the objectid parameter the endpoint takes
    parameter values: other values the endpoint takes 
    """
    if values is None:
        names_args = {}
    else:
        names_args = values.copy()
    
    names_args['_external'] = True
    if (isinstance(documents, dict)):
        _id = str(documents['_id'])
        del documents['_id']
        names_args[id_parameter_name]=_id
        documents['uri'] = url_for(endpoint,**names_args)
    elif (isinstance(documents, list)):
        for item in documents:
            hyperlink_ids(item, endpoint, id_parameter_name, **values)
    
    return documents
    