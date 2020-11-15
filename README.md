# django-base
A base with settings how I like them.

# Getting started

### Install Python 3:

```
% brew install python
```

Verify this works with `python3 --version` and `python3 -m pip -V`. You should see python 3.8 being used on both. If not, you may need to add `/usr/bin` to your PATH. 

### Create a virtual environment to install dependencies

```
% python3 -m venv env
# This may take a second
% source env/bin/activate
# Now the prompt should look like this:
(env) %
```

### Install dependencies

```
% python3 -m pip install -r requirements.txt
```

### Migrate

```
% python3 manage.py migrate
```

### Run the dev server

```
% python3 manage.py runserver
```

Visit localhost:8000 to verify the server is running correctly. 

