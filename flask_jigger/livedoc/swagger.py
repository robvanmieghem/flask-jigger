class SwaggerDoc(object):


    def generate(self):
        resourcelisting = {
            'apiVersion': "0.2",
            'swaggerVersion': "1.1",
            'basePath': "http://petstore.swagger.wordnik.com/api",
            'apis': [
                     {
                      'path': "/pet.{format}",
                      'description': "Operations about pets"
                      },
                     {
                      'path': "/user.{format}",
                      'description': "Operations about user"
                      }
                     ]
        }
        return resourcelisting;