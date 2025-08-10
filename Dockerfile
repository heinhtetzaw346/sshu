FROM rockylinux:9

RUN dnf install epel-release --assumeyes && \
		dnf install python3.12 python3.12-pip python3.12-devel --assumeyes

COPY requirement.txt /tmp/requirement.txt

RUN python3.12 -m venv /venv

RUN /venv/bin/pip install --upgrade pip && \
		/venv/bin/pip install -r /tmp/requirement.txt

RUN mkdir /dist

RUN mkdir sshu

COPY ./sshu sshu

ENTRYPOINT ["/venv/bin/python", "-m", "PyInstaller"]

CMD ["--name", "sshu", "--distpath", "/dist", "--onefile", "-p", "sshu", "sshu/cli.py"]

VOLUME /dist
