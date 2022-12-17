* root ip = 176.0.1.100 (client-1)
* zoonode ip = 176.0.1.99
* 
    ```
    docker run \
    -d --network host \
    -e HTTP_PORT=9000 \
    --name zoonavigator \
    --restart unless-stopped \
    elkozmon/zoonavigator:latest
    ```
* http://localhost:9000