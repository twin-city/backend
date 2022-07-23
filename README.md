# Docker Version

The docker image of this package is built with github action and stored [here](https://github.com/orgs/twin-city/packages/container/package/prepare-data).

- To build it locally :
```
docker build -t backend .
```

- To test is locally :
```
docker run -v $PWD/backend:/backend -v $PWD/tests:/tests -v $PWD/data:/data backend sh -c "pytest tests"
```

# backend

The package *backend* is served with fastapi, available in the docker image.

- To launch locally :
```
docker run --rm -p 8080:80 -v $PWD/app:/backend/app -v $PWD/data:/data --name backend-fastapi backend
```
- To test locally:
```
curl -X 'GET' 'http://localhost:8080/generate/?x1=649985&y1=6864006&x2=650266&y2=6864226' -H 'accept: application/json'
{"link": "https://.."}
```
