import sys
sys.path.insert(0, "/backend/app")

import hashlib
import pathlib
from typing import Optional
from kubernetes import config
from fastapi import FastAPI

from prepare_data.main import main
from prepare_data import utils
from pyproj import Proj, transform

from configmap import ConfigMapSecrets
from job import Job


app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "listen"}

@app.get('/delete/{job_name}')
def delete_job(job_name: str):
    try:
        job = Job(name=job_name)
        info = job.delete()
    except Exception as f:
        return 'Internal Error'
    return info

@app.get('/status/{job_name}')
def status_job(job_name: str):
    try:
        job = Job(name=job_name)
        info = job.get_job_status()
    except Exception as f:
        return 'Internal Error'
    return info

@app.get("/generate/")
def generate(x1: float, y1: float, x2: float, y2: float, job: bool = False,
                   crs: Optional[str] = None):
    # Convert to LAMBERT if needed
    name = hashlib.sha1(f'job-{y1}-{x1}-{y2}-{x2}').hexdigest()
    if not pathlib.Path(f"/data/{name}").exists():
        if crs:
            inProj = Proj('+init='+crs, preserve_units=True)
            outProj = Proj("+init=EPSG:2154")  # LAMBERT
            x1, y1 = transform(inProj, outProj, y1, x1)
            x2, y2 = transform(inProj, outProj, y2, x2)
        # Convert to shapely polygon
        try:
            polygon = utils.convert2poly(x1, y1, x2, y2)
            main(polygon, pathlib.Path(f'/data/{name}'))
        except Exception as f:
            return {"status": "KO", "reason": f}
    # start job
    if job:
        config.load_kube_config()
        _ = ConfigMapSecrets(name=name, from_path=f"/data/{name}")

        job_unity = Job(name=name,
                image="ghcr.io/twin-city/unity-project:os-unix-urp",
                cmd=["bash"],
                args=["-c", "git clone -b os/unix-urp https://github.com/twin-city/unity-project \
                    && cd unity-project \
                    && apt update && apt install -qy awscli python3-pip \
                    && pip3 install awscli-plugin-endpoint \
                    && mkdir /root/.aws \
                    && cp /config/config /root/.aws/ \
                    && cp /cred/credentials /root/.aws/ \
                    && chmod +x Assets/CommandeCLI/Run.sh Assets/CommandeCLI/upload-webgl.sh \
                    && Assets/CommandeCLI/Run.sh -d /unity-project \
                    -j /input -l /licence/Unity_v2020_pro2xs.x.ulf -b /output \
                    && Assets/CommandeCLI/upload-webgl.sh"],
                config=[name, 'licence', 'aws-cred', 'aws-conf'],
                env={"BUCKET_NAME": name},
                mount_path=['/input', '/licence', '/cred', '/config'],
                type_volume=["configmap", "configmap", "secret", "configmap"],
                pool_name="pool-gpu-3070-s"
                )

        status = job_unity.get_job_status()
        if 'succeeded' in status:
            return {'status': 'OK', "url": f"https://{name}.s3.fr-par.scw.cloud"}
        try:
            job_unity.start_job()
        except Exception as e:
            return {'status': 'KO', 'reason': e}
        return {"status": "OK", "job_name": name, "url": f'https://{name}.s3.fr-par.scw.cloud'}
    return {"status": "OK",
            "job_name": name,
            "url": f'https://{name}.s3.fr-par.scw.cloud',
            "warning": "no job launched"}

