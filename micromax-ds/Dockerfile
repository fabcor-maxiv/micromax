FROM mambaorg/micromamba:1.4.2

USER root
RUN apt-get update
RUN apt-get -y install supervisor nano

RUN micromamba install --name base --channel conda-forge \
    python=3.11.3 \
    sardana=3.4.0 \
    circus=0.18.0

# install our circus 'plug-in'
RUN mkdir /opt/circus
COPY tango_ping.py /opt/circus/

COPY circus.conf /etc/

RUN mkdir /tangods
COPY eiger.py /tangods/

CMD [ "/opt/conda/bin/circusd", "/etc/circus.conf" ]
