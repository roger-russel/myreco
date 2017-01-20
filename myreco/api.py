# MIT License

# Copyright (c) 2016 Diogo Dutra <dutradda@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from myreco.authorizer import MyrecoAuthorizer
from myreco.factory import ModelsFactory
from swaggerit.constants import SWAGGER_VALIDATOR
from swaggerit.aiohttp_api import AioHttpAPI
from swaggerit.exceptions import SwaggerItAPIError
from copy import deepcopy
import ujson


class MyrecoAPI(AioHttpAPI):
    def __init__(self, *, type_='recommender', sqlalchemy_bind=None, redis_bind=None,
                 swagger_json_template=None, title=None, version='1.0.0',
                 get_swagger_req_auth=True, loop=None, debug=False,
                 factory_class=ModelsFactory):
        self.models_factory = factory_class()
        self.all_models = self.models_factory.make_all_models(type_)
        authorizer = MyrecoAuthorizer(self.all_models['users'])
        models = [model for model in self.all_models.values() if hasattr(model, '__api__')]

        AioHttpAPI.__init__(
            self, models,
            sqlalchemy_bind=sqlalchemy_bind,
            redis_bind=redis_bind,
            swagger_json_template=swagger_json_template,
            title=title, version=version,
            authorizer=authorizer,
            get_swagger_req_auth=get_swagger_req_auth,
            loop=loop, debug=debug
        )
        self._set_items_models_routes(self.all_models['items_types'])

    def _set_items_models_routes(self, items_types_model):
        base_uri = '/{items_model_name}'
        handler = self._set_handler_decorator(items_types_model.items_models_handler)
        self._set_route(base_uri, 'GET', handler)
        self._set_route(base_uri, 'POST', handler)
        self._set_route(base_uri, 'PATCH', handler)
        self._set_route(base_uri + '/{item_key}', 'GET', handler)
        self._set_route(base_uri + '/{item_key}', 'POST', handler)

    def update_swagger_paths(self, model):
        SWAGGER_VALIDATOR.validate(model.__schema__)
        new_paths, definitions = self._get_model_paths_and_definitions(model)
        self.swagger_json['paths'].update(new_paths)
        self.swagger_json['definitions'].update(definitions)

    def remove_swagger_paths(self, model):
        new_swagger_json = deepcopy(self.swagger_json)
        paths_to_remove = set()
        definitions_to_remove = set()
        name = model.__name__

        for path in model.__schema__:
            if path != 'definitions':
                new_swagger_json['paths'].pop(path)
                paths_to_remove.add(path)

        for definition in list(new_swagger_json['definitions'].keys()):
            if name in definition:
                new_swagger_json['definitions'].pop(definition)
                definitions_to_remove.add(definition)

        [self.swagger_json['paths'].pop(path) for path in paths_to_remove]
        [self.swagger_json['definitions'].pop(path) for path in definitions_to_remove]
