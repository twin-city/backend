import os
import pathlib

from kubernetes import client
from kubernetes.client.rest import ApiException


class ConfigMap:
    def __init__(self, name, from_path=None, ns='default', metadata=None):
        """
        Create configmap from filepath: by a directory, a list of files or a specific file

        Usage example:
            a = ConfigMap(name='test', from_path='./configmap.py')
            print(a)
            a.delete()

        """
        self.name = name
        self.ns = ns
        self.metadata = metadata
        self.api_instance = client.CoreV1Api()

        self.obj = self._get_configmap_if_exist()
        if self.obj is None:
            configmap = self._create_object(path=from_path)
            self.obj = self._create(configmap)

        self.metadata = self.obj.metadata

    def __repr__(self):
        return str(self.obj)

    def _get_configmap_if_exist(self):
        """
        Check if configmap already exist in current namespace, if exist return there.
        """
        cm = self.api_instance.list_namespaced_config_map(namespace=self.ns)
        all_cm = [{"name": c["metadata"]["name"], 'index': n}
                  for n, c in enumerate(cm.to_dict()["items"])]
        for k in all_cm:
            if self.name == k["name"]:
                return cm.items[k["index"]]

    @staticmethod
    def _check_type(path):
        """
        Check type of path: list of files, directory, file, or nothing.
        """
        if not isinstance(path, (list, str)):
            return None
        elif isinstance(path, list):
            return path
        elif isinstance(path, str):
            if os.path.isdir(path):
                return [os.path.join(path, i) for i in os.listdir(path)]
            return [path]

    def read_data_from_file(self, path):
        """
        Create json content by reading all files
        """
        data = {}
        list_path = self._check_type(path)
        if list_path is not None:
            for file in list_path:
                with open(file, 'r') as f:
                    filename = pathlib.Path(file).name
                    data[filename] = f.read()
        return data

    def _create_object(self, path):
        """
        Prepare kubernetes configmap manifest (metadata and specs)
        """
        metadata = client.V1ObjectMeta(
            deletion_grace_period_seconds=30,
            name=self.name)

        if self.metadata is not None:
            metadata = metadata | self.metadata

        data = self.read_data_from_file(path)

        configmap = client.V1ConfigMap(
            api_version="v1",
            kind="ConfigMap",
            data=data,
            metadata=metadata
        )
        return configmap

    def _create(self, configmap):
        """
        Call kubernetes api for create configmap with an kubernetes configmap manifest
        """
        try:
            api_response = self.api_instance.create_namespaced_config_map(
                body=configmap,
                namespace=self.ns)
            return api_response

        except ApiException as e:
            print(f"Error when calling create configmap: {e}\n")

    def delete(self):
        """
        Delete if possible the current configmap
        """
        try:
            self.api_instance.delete_namespaced_config_map(
                namespace=self.ns, name=self.name)
            print(f'{self.name} configmap was deleted sucessfully')
        except ApiException as e:
            print(f"Error when calling delete configmap: {e}\n")


