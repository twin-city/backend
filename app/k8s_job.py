import sys
import os
import logging
import time
from time import sleep
from kubernetes import client

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('jobs')


class Job:
    def __init__(self, image="debian", namespace="default", kubeconfig_path=None):
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
        self.namespace = namespace
        self.info_jobs = {}

    def create_job_object(self, job_name, cmd="echo", args=None):
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
        # Configureate Pod template container
        container = client.V1Container(
            name=job_name,
            image=self.image,
            command=cmd if isinstance(cmd, list) else [cmd],
            args=args if isinstance(args, list) else [args]
            #volume_mounts=
            )

        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": job_name}),
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]))

        # Create the specification of deployment
        spec = client.V1JobSpec(
            template=template,
            backoff_limit=4)

        # Instantiate the job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=job_name),
            spec=spec)
        return job


    def start_job(self, job):
        self.info_jobs["start"] = time.time()
        #job = api_instance.read_namespaced_job(name=JOB_NAME, namespace=JOB_NS)
        api_response = self.api_instance.create_namespaced_job(
            body=job,
            namespace=self.namespace)
        logger.info(f"Job created. status={str(api_response.status)}")
        return api_response.status


    def get_job_status(self, job_name, follow=True, wait=1):
        while not self.job_completed:
            api_response = self.api_instance.read_namespaced_job_status(
                name=job_name,
                namespace=self.namespace)
            if api_response.status.succeeded is not None or \
                    api_response.status.failed is not None:
                self.job_completed = True
            self.info_jobs["current"] = time.time()
            logger.info(f"{self.info_jobs['current'] - self.info_jobs['start']} Job status={str(api_response.status)}")
            if not follow:
                # TODO: func
                info = api_response.status.to_dict()
                self.info_jobs["current"] = time.time()
                info["duration"] = self.info_jobs['current'] - self.info_jobs['start']
                return info
            sleep(wait)
        if self.job_completed:
            info = api_response.status.to_dict()
            self.info_jobs["current"] = time.time()
            info["duration"] = self.info_jobs['current'] - self.info_jobs['start']
            return info


    def delete_job(self, job_name):
        api_response = self.api_instance.delete_namespaced_job(
            name=job_name,
            namespace=self.namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        logger.info(f"Job deleted. Status={str(api_response.status)}")
        return api_response.status