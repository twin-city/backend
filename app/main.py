import sys
from typing import Optional

from fastapi import FastAPI

from prepare_data.main import main
from prepare_data import utils
from pyproj import Proj, transform

sys.path.insert(0, "/backend/app")
from k8s_job import start_process


app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "listen"}


@app.get("/generate/")
async def generate(x1: float, y1: float, x2: float, y2: float,
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

    # Creates the k8s job
    cmd = 'python'
    args = '--version'
    job_name = 'pi'
    start_process(job_name, cmd, args)

    return {"link": "https://.."}
