FROM python:3.10-slim
RUN pip install --upgrade pip
COPY . /usr/src/app
WORKDIR /usr/src/app
# Removes output stream buffering, allowing for more efficient logging
ENV PYTHONUNBUFFERED 1
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]



# FROM python:3.10
# COPY . /usr/src/app
# WORKDIR /usr/src/app
# RUN python -m venv /py && \
#     pip install --upgrade pip && \
#     pip install -r requirements.txt && \
#     adduser --disabled-password --no-create-home django-user

# # ENV PATH="/py/bin:$PATH"
# # Removes output stream buffering, allowing for more efficient logging
# ENV PYTHONUNBUFFERED 1
# # RUN pip install -r requirements.txt
# EXPOSE 8000
# USER django-user
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
# Gunicorn as app server
# CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app.wsgi:application
