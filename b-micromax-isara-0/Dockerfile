FROM mambaorg/micromamba:1.4.2

USER root
RUN apt-get update
RUN apt-get -y install nano

RUN micromamba install --name base --channel conda-forge \
    python=3.10.9

RUN mkdir /isara


COPY emu/*.py /isara/emu/
COPY overlord/*.py /isara/overlord/
COPY isara.py overlord.py /isara

WORKDIR /isara
CMD ["/isara/isara.py"]
