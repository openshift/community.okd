FROM registry.access.redhat.com/ubi8/ubi

RUN yum install -y make python3 python3-devel python3-pip python3-setuptools \
 && pip3 install --upgrade setuptools pip \
 && pip3 install \
      openshift \
      ansible \
      molecule

WORKDIR /src

COPY . /src

USER 1001
