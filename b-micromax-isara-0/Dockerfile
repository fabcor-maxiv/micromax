FROM mambaorg/micromamba:1.4.2

USER root
RUN apt-get update
RUN apt-get -y install nano

RUN micromamba install --name base --channel conda-forge \
    python=3.9.16

RUN mkdir /isara
COPY atcpserv.py emu.py /isara/

WORKDIR /isara

CMD [ "/isara/emu.py" ]
