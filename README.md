# docker-energy
Measuring the impact of the base image choice for different workloads inside Docker containers
```
sudo sh -c 'echo -1 >/proc/sys/kernel/perf_event_paranoid'
sudo sysctl -w kernel.perf_event_paranoid=-1
```