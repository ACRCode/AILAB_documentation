FROM python:3.9
RUN mkdir /app
COPY command.py /app/command.py
RUN pip3 install pymysql
RUN pip3 install boto3
RUN pip3 install boto3[crt]
RUN pip3 install pydicom
RUN apt update
RUN apt install --yes awscli
RUN chmod +x /app/command.py
CMD /app/command.py
