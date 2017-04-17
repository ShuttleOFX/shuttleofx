[![Stories in Ready](https://badge.waffle.io/shuttleofx/ShuttleOFX.png?label=ready&title=Ready)](https://waffle.io/shuttleofx/ShuttleOFX)
ShuttleOFX
==========

The ShuttleOFX platform is designed to share [OpenFX](http://openeffects.org) plugins between plugins creators (industrials, developpers, researchers, students, ...) and graphic artists. 
Following the [TuttleOFX](http://www.tuttleofx.org) initiative, the ambition is to promote a standard way to create image processing algorithms usable across softwares.

[![Stories in Ready](https://badge.waffle.io/shuttleofx/ShuttleOFX.png?label=ready&title=Ready)](http://waffle.io/shuttleofx/ShuttleOFX)
[![Stories in Progress](https://badge.waffle.io/shuttleofx/ShuttleOFX.png?label=in progress&title=In Progress)](http://waffle.io/shuttleofx/ShuttleOFX)

##### ShuttleOFX
>- website: [http://shuttleofx.org](http://shuttleofx.org)
>- github: [https://github.com/shuttleofx/ShuttleOFX](https://github.com/shuttleofx/ShuttleOFX)

##### TuttleOFX
>- website: [http://tuttleofx.org](http://tuttleofx.org)
>- github: [https://github.com/tuttleofx/TuttleOFX](https://github.com/tuttleofx/TuttleOFX)

##### OpenFX
>- website: [http://openeffects.org](http://openeffects.org)
>- github: [http://github.com/ofxa/openfx](http://github.com/ofxa/openfx)


License
-------
See [**COPYING.md**](COPYING.md)


Contact
-------

Use github issues for suggestions or bug report
> [http://github.com/shuttleofx/ShuttleOFX/issues](http://github.com/shuttleofx/ShuttleOFX/issues)


Development
-----------

Upload config files into `/etc/shuttleofx` and run the latest docker image.

##### Download the latest image

```
docker pull shuttleofx/shuttleofx
```

##### Local image build

Useful if you need to modify the Dockerfile.

```
docker build -t shuttleofx <source folder>
```

##### Run services

See [run_docker_dev.sh](run_docker_dev.sh) or [run_docker_server.sh](run_docker_server.sh)

##### Useful Docker options

 - **Interactive**: You can enter into the image with the option: ```-i --entrypoint /bin/bash```
 - **Clean image**: You can autoclean the image between runs: ```--rm=True```
