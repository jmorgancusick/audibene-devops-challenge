FROM python:3.7

RUN pip3 install pipenv

RUN useradd -m -s /bin/bash django

# wont be created by root, since already exists
WORKDIR /home/django

USER django

COPY --chown=django:django . .

RUN pipenv install

ENV PYTHONPATH "${PYTHONPATH}:/home/jenkins"

CMD ["pipenv", "run", "python3", "manage.py", "runserver", "0.0.0.0:8000"]
