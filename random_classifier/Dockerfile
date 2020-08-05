FROM python:3

RUN pip install numpy
RUN pip install argparse
RUN pip install pydicom
RUN pip install pandas
RUN pip install datetime

RUN pip install requests

ADD main.py .

ENTRYPOINT ["python", "main.py"]
