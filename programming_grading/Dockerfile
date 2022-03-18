# the grader image
#
# REQUIREMENTS:
# cgroups v2 rw mounted at /sys/fs/cgroup
# nsjail permissions

FROM docker.io/library/ubuntu:latest

# mostly requirements for nsjail.  could potentially include other stuff
# for other language graders
RUN apt-get -y update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    autoconf \
    bison \
    flex \
    gcc \
    g++ \
    git \
    libprotobuf-dev \
    libnl-route-3-dev \
    libtool \
    make \
    pkg-config \
    protobuf-compiler \
    python3 \
    python3-setuptools \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install grpcio protobuf google

# nsjail building
ADD nsjail /nsjail
RUN cd /nsjail && make && mv nsjail /bin && rm -rf /nsjail

# compile and install wait_on_cork --- must exist in the jails
ADD wait_on_cork.c .
RUN gcc wait_on_cork.c -o /bin/wait_on_cork && chmod 755 /bin/wait_on_cork && rm wait_on_cork.c

# install cmimc_programming library
ADD python_lib /python_lib
RUN cd /python_lib && pip3 install . && rm -rf /python_lib
