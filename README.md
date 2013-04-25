Flask-Jigger
============


The purpose of yet another rest thingy framework is just about not being a framework.

Goals are:
* not to impose any structure on consuming code
* keep Flask routing and functionality alone
* easy, fast creation of rest services without constantly duplicating your code
* support a browsable api

Usage
-----

Decorate functions decorated with `@app.route("/blablabla")` or used in an `add_url_rule` with the `api_view` decorator.

    from flask_jigger.views import api_view
    
    @api_view
    def someflaskviewfunction(id):
        return {'result':id}

If you want, you can also make your code more readable by using the status module:

    from flask_jigger.views import api_view
    from flask_jigger import status

    @api_view
    def someflaskviewfunction(id):
        abort(status.HTTP_400_BAD_REQUEST) #instead of abort(400)

Installation
------------

Flask-Jigger is listed on pypi and can be installed using pip:

`pip install Flask-Jigger`

