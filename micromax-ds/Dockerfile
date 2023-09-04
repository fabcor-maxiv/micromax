FROM mambaorg/micromamba:1.4.2

USER root
RUN apt-get update
RUN apt-get -y install nano

COPY condarc /opt/conda/.condarc

RUN micromamba install --name base --channel conda-forge \
    python=3.11.3 \
    sardana=3.4.0 \
    isara-ns-09-lib=1.1.0 \
    tangods-isara-ns-09=1.0.1 \
    circus=0.18.0

# install our circus 'plug-in'
RUN mkdir /opt/circus
COPY tango_ping.py /opt/circus/

COPY circus.conf /etc/

RUN mkdir /tangods
COPY eiger.py beam_shutter.py plc.py /tangods/

RUN mkdir /sardana_ctrls
COPY faux.py /sardana_ctrls/

CMD [ "/opt/conda/bin/circusd", "/etc/circus.conf" ]
