# PX4-Autopilot

[PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) PX4 is an open-source autopilot stack for drones and unmanned vehicles. It supports multirotors, fixed-wing, VTOL, rovers, and many more experimental platforms from racing quads to industrial survey aircraft. It runs on NuttX, Linux, and macOS. Licensed under BSD 3-Clause.

Setup **PX4-Autopilot** repository and install

``` shell
$ ansible-playbook jcook3701.docker.px4.yml -K
```

Remove **PX4-Autopilot** repository and uninstall

``` shell
$ ansible-playbook jcook3701.docker.px4.yml -K -e "action=uninstall"
```
