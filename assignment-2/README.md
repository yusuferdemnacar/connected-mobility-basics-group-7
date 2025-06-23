## Assignment 2

### Pi setup
#### Install docker:
```
$ curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh ./get-docker.sh
```

#### Add user to docker group
```
$ sudo groupadd docker; sudo usermod -aG docker $USER; newgrp docker
```

#### Check that everything is alright
`$ docker run hello-world` (you should see "Hello from Docker!")
