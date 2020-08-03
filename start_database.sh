docker run -d \
    --name database \
    -e POSTGRES_DB=database \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_USER=user \
    -p 5432:5432 \
    postgres
