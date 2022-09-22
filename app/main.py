import sys
import pathlib
from typing import Optional
from kubernetes import config
from fastapi import FastAPI

from prepare_data.main import main
from prepare_data import utils
from pyproj import Proj, transform

from configmap import Data
from job import Job

sys.path.insert(0, "/backend/app")

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "listen"}


@app.get("/generate/")
async def generate(x1: float, y1: float, x2: float, y2: float, job: bool = False,
                   crs: Optional[str] = None):
    # Convert to LAMBERT if needed
    if crs:
        inProj = Proj('+init='+crs, preserve_units=True)
        outProj = Proj("+init=EPSG:2154")  # LAMBERT
        x1, y1 = transform(inProj, outProj, y1, x1)
        x2, y2 = transform(inProj, outProj, y2, x2)
    # Convert to shapely polygon
    polygon = utils.convert2poly(x1, y1, x2, y2)
    main(polygon, pathlib.Path('/data'))

    # start job
    if job:
        config.load_kube_config()
        name = f'job-{y1}-{x1}-{y2}-{x2}'
        _ = Data(name=name, from_path=f"/data/{name}")

        job_unity = Job(
            name=name,
            image="ghcr.io/twin-city/unity-project:os-unix-urp",
            cmd=["bash"],
            args=["-c",
                  "/Assets/CommandeCLI/Run.sh \
                   -j /input -l /licence/Unity_v2020_pro2xs.x.ulf \
                   -b /output"],
            configmap=[name, 'licence'],
            mount_path=['/input', '/licence'])
        try:
            job_unity.start_job()
        except Exception as e:
            return {'Job failed': e}
        return {"status": "COMPLETED"}
    # TODO: use async for wait end of job to delete him: `job_instance.delete_job(name)`
    return {"status": "OK"}
