docker build -t service .
docker run -it --rm \
    --name service \
    -e DB_HOST="host.docker.internal" \
    -p 1234:1234 \
    service
