docker build -t service .
docker run -it --rm \
    --name service \
    -p 1234:1234 \
    service
