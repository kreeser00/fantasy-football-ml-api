FROM python:3
ARG mltarfile
WORKDIR /app
COPY . /app/
COPY ./app/main/controller.py /app/controller.py
COPY gunicorn_config.py /app/gunicorn_config.py
COPY fantasyfootballenv-lin64.yml /app/fantasyfootballenv-lin64.yml
COPY $mltarfile /app/
RUN conda env create -f fantasyfootballenv-lin64.yml -n fantasyfootballenv
RUN source activate fantasyfootballenv
RUN pip install $mltarfile
EXPOSE 5000
CMD []
#ENTRYPOINT ["python", "/app/controller.py"]
ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/app/gunicorn_config.py", "controller:app"]
