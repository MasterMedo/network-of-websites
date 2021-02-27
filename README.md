# network of websites

This is a dummy project to test the capabilities of the [memgraph](https://memgraph.com) database.
Given a *start* url and a *depth* `main.py network` scrapes all links from the *start* url with a max depth of *depth* and stores neighbouring websites in a graph database.
Given a *start* url and *end* url `main.py path` finds the shortest path from the *start* to *end* using the breadth-first-search built-in feature of memgraph and prints it to the screen.

# usage

Two main sub commands are provided in this repository; *network* and *path*.

### network
```
usage: main.py network [-h] [-d DEPTH] [start]

positional arguments:
  start                 start url (default: https://memgraph.com)

optional arguments:
  -h, --help            show this help message and exit
  -d DEPTH, --depth DEPTH
                        duration in seconds (default: 2)
example:
  python main.py network https://memgraph.com -d 4
```

### path
```
usage: main.py path [-h] [start] [end]

positional arguments:
  start       start url (default: https://memgraph.com)
  end         end url (default: https://github.com)

optional arguments:
  -h, --help  show this help message and exit

example:
  python main.py path https://facebook.com https://google.com
```

# testing
By running the `tester.py` file common tests will be conducted to ensure proper connection, valid memgraph setup and internal workings of the project.

# installation

There are no external dependencies, this project assumes a running server-side graph database.
Position yourself in the working directory and install dependencies with your favourite python package manager.


```
pip install -r requirements.txt
cp template.config.py config.py
```

Edit the `config.py` with your information and hack away!
