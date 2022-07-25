# Docker Version

Backend to serve [prepare_data](https://github.com/twin-city/prepare-data) package and launch kubernetes job.

- To build it locally :
```
docker build -t backend .
```

- To test is locally :
```
docker run -v $PWD/app:/backend/app -v $PWD/tests:/backend/tests -v $PWD/data:/data --env-file=.env  backend sh -c "pytest tests -s"
```

# backend

The package *backend* is served with fastapi, available in the docker image.

- To launch locally :
```
docker run --rm -p 8080:80 -v $PWD/app:/backend/app -v $PWD/data:/data  --env-file=.env DATA_PATH=/data  --name backend-fastapi backend
```
- To test locally:
```
curl -X 'GET' 'http://localhost:8080/generate/?x1=649985&y1=6864006&x2=650266&y2=6864226' -H 'accept: application/json'
{"link": "https://.."}
```
