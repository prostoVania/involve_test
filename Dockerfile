FROM python:3.7
ENV PYTHONBUFFERED 1
COPY . /involve
WORKDIR /involve
RUN pip3 install -r requirements.txt
#ENTRYPOINT ["python3.7"]
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]