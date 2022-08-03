import sys
import os
from typing import Optional
from kubernetes import config
from fastapi import FastAPI

from prepare_data.main import main
from prepare_data import utils
from pyproj import Proj, transform

sys.path.insert(0, "/backend/app")
from k8s_job import Job

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "listen"}


@app.get("/generate/")
async def generate(x1: float, y1: float, x2: float, y2: float, job: bool = False,
                crs: Optional[str] = None):
    # Convert to LAMBERT if needed
    if crs :
        inProj  = Proj('+init='+crs, preserve_units=True)
        outProj = Proj("+init=EPSG:2154") #  LAMBERT
        x1, y1 = transform(inProj, outProj, y1, x1)
        x2, y2 = transform(inProj, outProj, y2, x2)
    # Convert to shapely polygon
    polygon = utils.convert2poly(x1, y1, x2, y2)
    main(polygon)

    # start job
    if job:
        config.load_kube_config()
        # Creates the k8s job
        name = f'test-{y1}-{x1}-{y2}-{x2}'
        job_instance = Job(image="debian", namespace="twincity")
        template = job_instance.create_job_object(name)
        try:
            job_instance.start_job(template)
            info = job_instance.get_job_status(name, follow=False)
        except Exception as e:
            return {'Job failed': e}
        return info
    # TODO: use async for wait end of job to delete him: `job_instance.delete_job(name)`
    return {"status": "OK"}
