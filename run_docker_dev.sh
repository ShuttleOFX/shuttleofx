# 
## Allow sub-dockers:
# Use '-v' 'docker' and 'docker.sock' to share docker with the main one
#
## Ensure more ressources for the server than for rendering tasks
# Use 'cpu-shares=4096' which 4x more than the default value of 1024 used for sub-dockers for rendering.
#

sudo docker run -td --name shuttleofx_cnt \
-p 80:5000 -p 5004:5004 -p 5002:5002 -p 5005:5005 -p 27017:27017 \
-v $PWD:/opt/shuttleofx_git \
-v /var/log/shuttleofx:/var/log/shuttleofx \
-v /opt/mongo-data:/opt/mongo-data \
-v /opt/shuttleofx:/opt/shuttleofx \
-v /etc/shuttleofx:/etc/shuttleofx \
-v /var/run/docker.sock:/run/docker.sock \
-v /tmp:/tmp \
--cpu-shares=4096 \
shuttleofx/shuttleofx-develop
