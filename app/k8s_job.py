from argparse import Namespace
from kubernetes import client, config
from time import sleep
import os

JOB_NS=os.environ.get('JOB_NS', '')
IMAGE=os.environ.get('IMAGE', '')
KUBECONFIG=os.environ.get('KUBECONFIG', '')
KUBECONFIG_FILE="/tmp/kubeconfig.yaml"

def create_job_object(job_name, cmd, args):
    # Configureate Pod template container
    container = client.V1Container(
        name=job_name,
        image=IMAGE,
        command=[cmd, args])
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


def create_job(api_instance, job):
    #job = api_instance.read_namespaced_job(name=JOB_NAME, namespace=JOB_NS)
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace=JOB_NS)
    print("Job created. status='%s'" % str(api_response.status))
    get_job_status(api_instance)


def get_job_status(api_instance, job_name):
    job_completed = False
    while not job_completed:
        api_response = api_instance.read_namespaced_job_status(
            name=job_name,
            namespace=JOB_NS)
        if api_response.status.succeeded is not None or \
                api_response.status.failed is not None:
            job_completed = True
        sleep(1)
        print("Job status='%s'" % str(api_response.status))

def delete_job(api_instance, job_name):
    api_response = api_instance.delete_namespaced_job(
        name=job_name,
        namespace=JOB_NS,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print("Job deleted. status='%s'" % str(api_response.status))

def save_kubeconfig():
    file=open(KUBECONFIG_FILE)
    file.write(KUBECONFIG)


def start_process(job_name, cmd, args):
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    save_kubeconfig()
    config.load_kube_config(config_file=KUBECONFIG_FILE)
    batch_v1 = client.BatchV1Api()
    # Create a job object with client-python API. The job we
    # created is same as the `pi-job.yaml` in the /examples folder.
    job = create_job_object(job_name, cmd, args)
    #update_job(batch_v1, job)
    create_job(batch_v1, job)
    get_job_status(batch_v1, job_name)
    delete_job(batch_v1, job_name)
