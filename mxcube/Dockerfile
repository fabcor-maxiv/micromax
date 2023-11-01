FROM mambaorg/micromamba:1.5.1

USER root
RUN apt-get update
RUN apt-get -y install \
    # need for lucid3
    libgl1-mesa-glx \
    iputils-ping git nano

COPY condarc /opt/conda/.condarc

RUN micromamba install --name base --channel conda-forge \
    python=3.9.16 \
    pytango=9.4.1 \
    itango=0.1.9 \
    redis-server=7.0.11 \
    circus=0.18.0 \
    # install as conda package, so pip does not try to compile it
    python-ldap=3.4.0 \
    # for building front-end \
    nodejs=18.15.0 \
    # MAXIV specific packages for MXCube
    sdm=1.8.8 \
    sardana=3.4.0

#
# clone mxcube repositories
#

RUN mkdir /app
WORKDIR /app

# 'Core' repository
RUN git clone --branch maxiv-develop https://gitlab.maxiv.lu.se/kits-maxiv/mxcube/mxcubecore.git core
# pin to specified commit
RUN cd core && git checkout 0c25efe58b9934ccf874b22395ab28f83b5285bb


# 'Web' aka main repository
RUN git clone --branch maxiv-develop https://gitlab.maxiv.lu.se/kits-maxiv/mxcube/mxcube3.git web
# pin to specified commit
RUN cd web && git checkout 07deed0b0944fbef0c4f0fd121e6b8667621132d

# 'Configuration' repsitory
RUN git clone --branch maxiv-micromax https://gitlab.maxiv.lu.se/kits-maxiv/mxcube/cfg-maxiv-mxcubecore.git conf
# pin to specified commit
RUN cd conf && git checkout 24816d8952e9ce372629ab21610b1d509c4e3230

# remove web proxy from ISPyB configuration, to avoid emulating web proxy.
# ISPyB is accessable without proxy on white network.
COPY no_lims_proxy.patch /tmp
RUN cd conf && git apply /tmp/no_lims_proxy.patch

# remove 'mxcubecore' and 'mxcube_video_streamer' packages from dependencies
RUN sed -i '/^mxcubecore\|^mxcube_video_streamer/d' web/pyproject.toml
RUN /opt/conda/bin/pip install -e web
RUN /opt/conda/bin/pip install -e core

# build front-end
WORKDIR /app/web/ui
RUN /bin/micromamba run -p /opt/conda npm install
RUN /bin/micromamba run -p /opt/conda npm run build

# install convenience script for running mxcube from terminal
COPY run.sh /app/

# install our circus 'plug-in'
RUN mkdir /opt/circus
COPY tango_ping.py /opt/circus/

COPY circus.conf /etc/

WORKDIR /app
CMD [ "/opt/conda/bin/circusd", "/etc/circus.conf" ]
