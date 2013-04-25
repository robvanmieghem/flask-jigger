flask-jigger
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

`
    from flask_jigger import api_view
    
    @api_view
    def someflaskviewfunction(id):
        return {'result':id}
`


