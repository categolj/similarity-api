
```
mkdir -p .local/blog-db
echo -n postgresql > .local/blog-db/type
echo -n 127.0.0.1 > .local/blog-db/host
echo -n 5433 > .local/blog-db/port
echo -n postgresml > .local/blog-db/username
echo -n "" > .local/blog-db/password
echo -n postgresml > .local/blog-db/database

docker-compose up
```
