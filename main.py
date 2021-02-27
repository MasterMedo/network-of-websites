import signal
import requests

from collections import deque
from argparse import ArgumentParser, RawTextHelpFormatter
from requests.exceptions import RequestException, ConnectionError
from bs4 import BeautifulSoup
from neo4j import GraphDatabase

from config import uri, username, password, headers
from utils import timeit, timeout_handler  # noqa
from exceptions import WebsiteNotFoundError, ShortestPathNotFoundError


signal.signal(signal.SIGALRM, timeout_handler)


def network(start, depth, driver, **kwargs):
    """Uses breadth first search to find all the websites `depth` jumps away
    from the next website. Stores newly found nodes in the graph database using
    the `driver` argument.
    """
    if depth < 0:
        raise ValueError(f'Depth must be 0 or larger, was {depth}')

    start = start.rstrip('/')
    if not is_url_valid(start):
        raise WebsiteNotFoundError(start)

    with driver.session() as session:
        session.write_transaction(create_url, start, depth)

    if depth == 0:
        return
    visit = deque([(start, depth)])

    while visit:
        start, depth = visit.pop()
        with driver.session() as session:
            if not session.read_transaction(exists, start).single():
                build_network(start, depth, driver, visit)
                continue

            links = session.read_transaction(get_links, start)
            if not links.peek():
                build_network(start, depth, driver, visit)
                continue

            visit.extend([(a.get('name'), depth - 1)
                          for a in links if a.get('depth') < depth - 1])


def path(start, end, driver, **kwargs):
    """Gets the shortest path between `start` and `end` urls if they are
    present in the graph database queried using the `driver` argument.
    If urls are not present raises `WebsiteNotFoundError`.
    If the path does not exist raises `ShortestPathNotFoundError`.
    """
    with driver.session() as session:
        if not session.read_transaction(exists, start).single():
            raise WebsiteNotFoundError(start)

        if not session.read_transaction(exists, end).single():
            raise WebsiteNotFoundError(end)

        path = session.read_transaction(get_path, start, end)
        if not path.peek():
            raise ShortestPathNotFoundError(f'{start}, {end}')

        path = path.single().get('path')
        print(f'The node is {len(path) - 1} jumps away:')
        for node in path:
            print(f"  {node.get('name')}")


def build_network(start, depth, driver, visit, timeout=1):
    """Scrapes all links on the `start` url.
    In case of an `RequestException` or `TimeoutError` does nothing.
    """
    with driver.session() as session:
        session.write_transaction(create_url, start, depth)

    try:
        signal.alarm(3)
        r = requests.get(start, headers=headers, timeout=timeout)
        soup = BeautifulSoup(r.text, 'html.parser')
        signal.alarm(0)
    except (RequestException,
            IndexError,
            ConnectionError,
            TimeoutError):
        return

    for link in soup.find_all('a', href=True):
        end = link['href'].split('?', 1)[0].rstrip('/')
        if not end or end.startswith('/'):
            end = start + end

        if start != end:
            with driver.session() as session:
                session.write_transaction(create_link, start, end, depth - 1)

            if depth - 1 > 0:
                visit.append((end, depth - 1))


def is_url_valid(url):
    try:
        return requests.head(url, timeout=1).status_code == 200
    except RequestException:
        return False


def exists(tx, start):
    return tx.run("match (a: Url)"
                  "where a.name = $start "
                  "return a as url",
                  start=start)


def get_depth(tx, start):
    return tx.run("match (a: Url) "
                  "where a.name = $start "
                  "return a.depth as depth",
                  start=start)


def get_links(tx, start):
    return tx.run("match (a: Url {name: $start}) - [r: Links] -> (b: Url)"
                  "return b.name as name, b.depth as depth",
                  start=start)


def create_url(tx, start, depth):
    return tx.run("merge (a: Url {name: $start}) "
                  "set a.depth = $depth",
                  start=start, depth=depth)


def create_link(tx, start, end, depth):
    tx.run("merge (a: Url {name: $start})"
           "merge (b: Url {name: $end})"
           "set b.depth = $depth "
           "merge (a)-[:Links]->(b)",
           start=start, end=end, depth=depth)


def get_path(tx, start, end):
    return tx.run("MATCH p = (:Url {name: $start}) - [:Links * bfs] -> (:Url {name: $end})"
                  "RETURN nodes(p) as path",
                  start=start, end=end)


def parse_args():
    """Parses `sys.argv` and returns args suitable for sub commands."""
    default = '(default: %(default)s)'
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    subparsers = parser.add_subparsers(required=True, dest='function')

    network_parser = subparsers.add_parser('network')
    network_parser.set_defaults(func=network)
    network_parser.add_argument('start', type=str, nargs='?',
                                default='https://memgraph.com',
                                help='start url ' + default)
    network_parser.add_argument('-d', '--depth', type=int, default=2,
                                help='duration in seconds ' + default)

    path_parser = subparsers.add_parser('path')
    path_parser.set_defaults(func=path)
    path_parser.add_argument('start', type=str, nargs='?',
                             default='https://memgraph.com',
                             help='start url ' + default)
    path_parser.add_argument('end', type=str, nargs='?',
                             default='https://github.com',
                             help='end url ' + default)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    driver = GraphDatabase.driver(uri, auth=(username, password), secure=True)
    args.func(driver=driver, **vars(args))
    driver.close()
