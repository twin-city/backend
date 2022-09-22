import os
import pathlib
import base64
from kubernetes import client


class Data:
    def __init__(
            self, name, kind='secret', from_path=None, ns='default',
            metadata=None):
        """
        Create configmap or secret from filepath: by a directory, \
            a list of files or a specific file

        Usage example:
            a = ConfigMap(name='test', kind='secret', from_path='./configmap.py')
            print(a)
            a.delete()

        """
        self.name = name
        self.ns = ns
        self.metadata = metadata
        self.api_instance = client.CoreV1Api()
        self.kind = kind
        self.encode = True if self.kind == 'secret' else False
        self.dict_values = {'secret': {'list': 'list_namespaced_secret',
                                       'object': 'V1Secret',
                                       'resource': 'Secret',
                                       'create': 'create_namespaced_secret',
                                       'delete': 'delete_namespaced_secret'},
                            'configmap': {'list': 'list_namespaced_config_map',
                                          'object': 'V1ConfigMap',
                                          'create': 'create_namespaced_config_map',
                                          'resource': 'ConfigMap',
                                          'delete': 'delete_namespaced_config_map'}
                            }
        self.obj = self._get_if_exist()
        if self.obj is not None:
            self.delete(msg='replace')
        data_conf = self._create_object(path=from_path)
        self.obj = self._create(data_conf)
        #self.metadata = self.obj.metadata

    def __repr__(self):
        return str(self.obj)

    def _get_if_exist(self):
        cm = getattr(self.api_instance, self.dict_values[self.kind][
            "list"])(namespace=self.ns)
        all_cm = [{"name": c["metadata"]["name"], 'index': n
                   } for n, c in enumerate(cm.to_dict()["items"])]
        for k in all_cm:
            if self.name == k["name"]:
                return cm.items[k["index"]]

    @staticmethod
    def _check_type(path):
        """
        Check type of path: one file, dir or list of files
        """
        if not isinstance(path, (list, str)):
            return None
        elif isinstance(path, list):
            return path
        elif isinstance(path, str):
            if os.path.isdir(path):
                return [os.path.join(path, i) for i in os.listdir(path)]
            return [path]

    @classmethod
    def read_data_from_file(cls, path, encode: bool=False):
        """
        Read data from file. For secret it's possible to encode them
        """
        data = {}
        list_path = cls._check_type(path)
        if list_path is not None:
            for file in list_path:
                with open(file, 'r') as f:
                    filename = pathlib.Path(file).name
                    data[filename] = f.read() if not encode else base64.b64encode(
                        str.encode(f.read())).decode('utf-8')
        return data

    def _create_object(self, path):
        """
        Prepare kubernetes object
        """
        metadata = client.V1ObjectMeta(
            deletion_grace_period_seconds=30,
            name=self.name)

        if self.metadata is not None:
            metadata = metadata | self.metadata

        data = self.read_data_from_file(path, self.encode)

        yaml = getattr(client, self.dict_values[self.kind]["object"])(
            api_version="v1",
            kind=self.dict_values[self.kind]["resource"],
            data=data,
            metadata=metadata
        )
        return yaml

    def _create(self, yaml_object):
        """
        Create configmap/secret
        """
        try:
            api_response = getattr(self.api_instance,
                                   self.dict_values[self.kind]["create"])(
                body=yaml_object,
                namespace=self.ns
            )
            return api_response

        except client.rest.ApiException as e:
            print(f"Error when calling create {self.kind}: {e}\n")

    def delete(self, msg='delete'):
        """
        Delete current configmap/secret
        """
        try:
            getattr(self.api_instance, self.dict_values[self.kind]["delete"])(
                namespace=self.ns, name=self.name)
            print(f'{self.name} {self.kind} was {msg}d sucessfully')
        except client.rest.ApiException as e:
            print(f"Error when calling {msg} {self.kind}: {e}\n")
