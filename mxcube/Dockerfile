FROM mambaorg/micromamba:1.4.2

USER root
RUN apt-get update
RUN apt-get -y install iputils-ping git nano

COPY condarc /opt/conda/.condarc

RUN micromamba install --name base --channel conda-forge \
    python=3.9.16 \
    pytango=9.4.1 \
    itango=0.1.9 \
    redis-server=7.0.11 \
    circus=0.18.0 \
    # install as conda package, so pip does not try to compile it
    python-ldap=3.4.0 \
    # MAXIV specific packages for MXCube
    sdm=1.8.8 \
    sardana=3.4.0

#
# clone mxcube repositories
#

RUN mkdir /app
WORKDIR /app

# 'Core' repository
RUN git clone --branch maxiv-micMax https://gitlab.maxiv.lu.se/kits-maxiv/mxcube/mxcubecore.git core
# pin to specified commit
RUN cd core && git checkout f521c6038b5b1a97f4358c2390df101f7edfd305

# 'Web' aka main repository
RUN git clone --branch develop https://gitlab.maxiv.lu.se/kits-maxiv/mxcube/mxcube3.git web
# pin to specified commit
RUN cd web && git checkout 35d62cbc989953d22c6752a2d6e1204babc4979b

# 'Configuration' repsitory
RUN git clone --branch maxiv-micromax https://gitlab.maxiv.lu.se/kits-maxiv/mxcube/cfg-maxiv-mxcubecore.git conf

# pin to specified commit
RUN cd conf && git checkout 966edbddb85fed47d182360f2510331683976ff1

# remove web proxy from ISPyB configuration, to avoid emulating web proxy.
# ISPyB is accessable without proxy on white network.
COPY no_lims_proxy.patch /tmp
RUN cd conf && git apply /tmp/no_lims_proxy.patch

# remove 'mxcubecore' and 'mxcube_video_streamer' packages from dependencies
RUN sed -i '/^mxcubecore\|^mxcube_video_streamer/d' web/pyproject.toml
RUN /opt/conda/bin/pip install -e web

RUN /opt/conda/bin/pip install -e core

# install our circus 'plug-in'
RUN mkdir /opt/circus
COPY tango_ping.py /opt/circus/

COPY circus.conf /etc/


CMD [ "/opt/conda/bin/circusd", "/etc/circus.conf" ]
