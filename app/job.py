import sys
import os
import logging
import time
from time import sleep
from kubernetes import client

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('jobs')


class Job:
    def __init__(self,
                 name,
                 image,
                 cmd,
                 namespace="default",
                 args=None,
                 configmap=None,
                 mount_path=None,
                 **kwargs):
        """
        Make a job in a kubernetes cluster
        WARNING: must run command `config.load_kube_config()`

        Parameters
        ----------
        image : str, image used for pod
        namespace : str, namespace where job is launch
        kubeconfig_path : str, optional, kubeconfig path, by default None
        """
        self.job_completed = False
        self.api_instance = client.BatchV1Api()
        self.image = image
        self.job_name = name
        self.cmd = cmd
        self.args = args
        self.namespace = namespace
        self._info_jobs = {}
        self.configmap = configmap
        self.mount_path = mount_path
        self.kwargs = kwargs
        self.job = self._create_job_object()

    def __repr__(self):
        return str(self.job)

    def _create_volumes(self):
        """
        Create volume yaml part for job template
        """
        if self.configmap is None or self.mount_path is None:
            return None, None

        self.configmap = [self.configmap] if isinstance(
            self.configmap, str) else self.configmap
        self.mount_path = [self.mount_path] if isinstance(
            self.mount_path, str) else self.mount_path

        if len(self.configmap) != len(self.mount_path):
            print('Mismatch configmaps and volumes mounts')
            return None, None

        l_volume, l_volumemount = [], []
        for cm, vm in zip(self.configmap, self.mount_path):
            volume = client.V1Volume(
                name=f'volume-{cm}',
                config_map=client.V1ConfigMapVolumeSource(name=cm)
            )
            volume_mount = client.V1VolumeMount(
                mount_path=vm,
                name=f'volume-{cm}',
                read_only=self.kwargs["read_only"] if
                "read_only" in self.kwargs else None
            )
            l_volume.append(volume), l_volumemount.append(volume_mount)

        return l_volume, l_volumemount

    def _create_job_object(self):
        """
        Create Job object
        Parameters
        ----------
        job_name : str, name of job
        cmd : str, optional, command used for entrypoint
        args : str, optional, args for entrypoints, by default None

        Returns
        -------
        V1Job: template for a job
        """

        # Mount volume
        volume, volume_mount = self._create_volumes()

        # Configureate Pod template container
        container = client.V1Container(
            name=self.job_name,
            image=self.image,
            command=self.cmd if isinstance(self.cmd, list) else [self.cmd],
            args=self.args if isinstance(self.args, list) else [self.args],
            volume_mounts=volume_mount
        )

        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": self.job_name}),
            spec=client.V1PodSpec(
                restart_policy="Never",
                containers=[container],
                volumes=volume)
        )

        # Create the specification of deployment
        spec = client.V1JobSpec(
            template=template,
            backoff_limit=4)

        # Instantiate the job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=self.job_name),
            spec=spec
        )
        return job

    def start_job(self):
        """
        Start kubernetes job. It's possible to see template with `job` attribute
        """
        self._info_jobs["start"] = time.time()
        api_response = self.api_instance.create_namespaced_job(
            body=self.job,
            namespace=self.namespace)
        #logger.info(f"Job created. status={str(api_response.status)}")
        return api_response.status

    def get_job_status(self, follow=True, wait=1):
        """
        See logs for current job

        Parameters
        ----------
        follow : bool, optional
            follow logs, by default True
        wait : int, optional
            time in seconds between refresh, by default 1
        """
        while not self.job_completed:
            api_response = self.api_instance.read_namespaced_job_status(
                name=self.job_name,
                namespace=self.namespace)
            if api_response.status.succeeded is not None or \
                    api_response.status.failed is not None:
                self.job_completed = True
            self._info_jobs["current"] = time.time()
            #logger.info(f"{self._info_jobs['current'] - self._info_jobs['start']} Job status={str(api_response.status)}")
            if not follow:
                # TODO: func
                info = api_response.status.to_dict()
                self._info_jobs["current"] = time.time()
                info["duration"] = self._info_jobs['current'] - self._info_jobs['start']
                return info
            sleep(wait)
        if self.job_completed:
            info = api_response.status.to_dict()
            self._info_jobs["current"] = time.time()
            info["duration"] = self._info_jobs['current'] - self._info_jobs['start']
            return info

    def delete_job(self):
        """
        Delete current job
        """
        api_response = self.api_instance.delete_namespaced_job(
            name=self.job_name,
            namespace=self.namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        #logger.info(f"Job deleted. Status={str(api_response.status)}")
        return api_response.status
