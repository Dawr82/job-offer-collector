$build = $args[0]

if ($build -eq 1){
    docker build -t flask-api .
}

docker rm -f flask-api
docker run -d -p 8080:5000 --name flask-api flask-api
docker ps 

