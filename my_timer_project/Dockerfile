###########
# BUILDER #
###########

# pull official base image
FROM python:3.10.4-slim-bullseye as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update \
    && apt-get install -y gcc python3-dev musl-dev

# lint
RUN pip install --upgrade pip
RUN pip install flake8==3.9.2
COPY . .
# RUN flake8 --ignore=E501,F401 .

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.10.4-slim-bullseye

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system app --ingroup app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update \
     && apt -y install wkhtmltopdf

# COPY ./../wkhtmltopdf_distr/wkhtmltopdf /bin/
# COPY ./../wkhtmltopdf_distr/simsun.ttc /usr/share/fonts/chinese/TrueType/
# COPY ./../wkhtmltopdf_distr/simsun.ttf /usr/share/fonts/chinese/TrueType/ 

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy entrypoint.prod.sh
COPY ./entrypoint.prod.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.prod.sh
RUN chmod +x  $APP_HOME/entrypoint.prod.sh

# copy project
COPY . $APP_HOME

# copy wkhtmltopdf
# RUN mv ./wkhtmltopdf_distr/wkhtmltopdf /bin/
# RUN mv ./wkhtmltopdf_distr/simsun.ttc /usr/share/fonts/chinese/TrueType/
# RUN mv ./wkhtmltopdf_distr/simsun.ttf /usr/share/fonts/chinese/TrueType/ 
# RUN chmod +x /bin/wkhtmltopdf 
# RUN mkdir -p /usr/share/fonts/chinese/TrueType/

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run entrypoint.prod.sh
ENTRYPOINT ["/home/app/web/entrypoint.prod.sh"]