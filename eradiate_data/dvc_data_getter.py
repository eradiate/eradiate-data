import dvc
import dvc.api
import os

from .core import DataGetter
from . import path_resolver

class DVCDataGetter(DataGetter):

    revision=None
    repository="https://github.com/eradiate/eradiate-data.git"
    revision="dvc-setup"

    @classmethod
    def gather_file(path):
        url = dvc.api.get_url(path, repo=repository, rev=revision, mode="rb")
        if len(path_resolver.paths) == 0:
            raise ValueError("Invaild path to the data folder")
        data_path = path_resolver.paths[0]
        r = requests.get(url, allow_redirects=True)
        open(data_path / path, 'wb').write(r.content)

    @classmethod
    def gather_all():
        for path in PATHS.values():
            gather_file(path)
    
    @classmethod
    def find(cls):
        result = {}

        for id in cls.PATHS.keys():
            path = _presolver.resolve(cls.path(id))
            result[id] = path.is_file()

        return result
