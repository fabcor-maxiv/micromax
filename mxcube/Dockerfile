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
    pnpm=8.6.5 \
    # MAXIV specific packages for MXCube
    sdm=1.8.8 \
    sardana=3.4.0

#
# clone mxcube repositories
#

RUN mkdir /app
WORKDIR /app

# clone 'Core' repository and pin to specific commit
RUN git clone --branch maxiv-develop https://gitlab.maxiv.lu.se/kits-maxiv/mxcube/mxcubecore.git core && \
    cd core && \
    git checkout a7def25b37b8a2fb0c4645af8fbbc9d01cb1b913

# clone 'Web' aka main repository and pin to specific commit
RUN git clone --branch maxiv-develop https://gitlab.maxiv.lu.se/kits-maxiv/mxcube/mxcube3.git web && \
    cd web && \
    git checkout 1fc58f4e5dfe9321db5d8efb1e53e2c12533e7f6

# clone 'Configuration' repsitory and pin to specific commit
RUN git clone --branch maxiv-micromax https://gitlab.maxiv.lu.se/kits-maxiv/mxcube/cfg-maxiv-mxcubecore.git conf && \
    cd conf && \
    git checkout e8a8af082d11ac47d52a7eff6df49720030d9cdc

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
RUN /bin/micromamba run -p /opt/conda pnpm remove 'cypress' '@testing-library/cypress'
RUN /bin/micromamba run -p /opt/conda pnpm install
RUN /bin/micromamba run -p /opt/conda pnpm run build

# move generated UI files outside of git repository,
# this way we can mount over /app/web directory
# from outside, if needed, for editing purpuses
RUN mkdir /opt/mxcube
RUN mv /app/web/ui/build /opt/mxcube

# install convenience script for running mxcube from terminal
COPY run.sh /app/

# install our circus 'plug-in'
RUN mkdir /opt/circus
COPY tango_ping.py /opt/circus/

COPY circus.conf /etc/

WORKDIR /app
CMD [ "/opt/conda/bin/circusd", "/etc/circus.conf" ]
