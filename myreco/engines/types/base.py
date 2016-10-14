# MIT License

# Copyright (c) 2016 Diogo Dutra

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


from falconswagger.models.base import build_validator, get_module_path
from jsonschema import Draft4Validator
from abc import ABCMeta, abstractmethod
import inspect


class EngineTypeMeta(type):

    def __init__(cls, name, bases_classes, attributes):
        if name != 'EngineType':
            schema = cls.__configuration_schema__
            Draft4Validator.check_schema(schema)
            cls.__config_validator__ = build_validator(schema, get_module_path(cls))


class EngineType(metaclass=EngineTypeMeta):
    def __init__(self, engine):
        self.__config_validator__.validate(engine['configuration'])
        self._validate_config(engine)
        self.engine = engine

    def get_variables(self):
        return []

    def _validate_config(self, engine):
        pass

    def get_recommendations(self, **variables):
        return []

    def export_objects(self, session):
        pass


class AbstractDataImporter(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def get_data(cls, engine):
        pass


from myreco.engines.types.neighborhood.engine import NeighborhoodEngine
from myreco.engines.types.top_seller.engine import TopSellerEngine
from myreco.engines.types.visual_similarity.engine import VisualSimilarityEngine


class EngineTypeChooser(object):

    def __new__(cls, name):
        if name == 'neighborhood':
            return NeighborhoodEngine

        elif name == 'top_seller':
            return TopSellerEngine

        elif name == 'visual_similarity':
            return VisualSimilarityEngine
