import heapq
from queue import Queue

from py_wikiracer.internet import Internet
from typing import List
from html.parser import HTMLParser

class Parser:

    @staticmethod
    def get_links_in_page(html: str) -> List[str]:
        """
        In this method, we should parse a page's HTML and return a list of links in the page.
        Be sure not to return any link with a DISALLOWED character.
        All links should be of the form "/wiki/<page name>", as to not follow external links.

        To do this, you can use str.find, regex, or you can
            instantiate your own subclass of HTMLParser in this function and feed it the html.
        """
        links = []
        disallowed = Internet.DISALLOWED

        # YOUR CODE HERE
        # Make sure your list doesn't have duplicates. Return the list in the same order as they appear in the HTML.
        # You can define your subclass of HTMLParser right here inside this function, or you could do it outside of this function.

        # This function will be mildly stress tested.

        # Returns html code for a given page.
        # Filters out disallowed & external links\

        class WikiParser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                """
                Overriding the current function in HTMLParser to look at only <a> starter tags
                Called automatically by HTMLParser whenever a start tag <> is encountered
                """
                if tag == 'a':
                    for attr, value in attrs:
                        # Processes only hyperlinks (href), no duplicate links, no external links outside wiki & no disallowed characters (value[6:] ignores "/wiki/")
                        if attr == 'href' and value not in links and value.startswith('/wiki/') and not any(char in value[6:] for char in disallowed):
                            links.append(value)

        parser = WikiParser()
        parser.feed(html)
        return links

# In these methods, we are given a source page and a goal page, and we should return
#  the shortest path between the two pages. Be careful! Wikipedia is very large.

# These are all very similar algorithms, so it is advisable to make a global helper function that does all of the work, and have
#  each of these call the helper with a different data type (stack, queue, priority queue, etc.)
def search(internet:Internet, source: str, goal: str, algorithm: str, costFn = None):
    """
    Uses either the bfs, dfs, or Dijkstra's search algorithm in order to find the shortest path to go from the source to goal node.
    """
    # Step 1: Initialize
    path = [source]
    visited = set()

    # Step 2: Use a stack, queue, or priority queue/min-heap for generic container depending on the search algorithm
    # Add the root to the container; (starting node, list that tracks the sequence of nodes visited)
    if algorithm == "dfs":
        container = [] #stack
        container.append((source,path))
    elif algorithm == "bfs":
        container = Queue() #queue
        container.put((source, path))
    else:
        container = [] #priority queue
        # Inserts tuple (cost of reaching node, starting node, list that tracks the sequence of nodes visited) into the pq, which is implemented as a min-priority heap (heapq)
        heapq.heappush(container,(0,source, path))
        if algorithm == "wikiracer":
            goal_links = set(Parser.get_links_in_page(internet.get_page(goal)))
            # Identify common links using Internet.get_random
            common_links = set()
            common_links_counts = {}
            for _ in range(3):
                links = Parser.get_links_in_page(internet.get_random())
                for link in links:
                    common_links_counts[link] = common_links_counts.get(link, 0) + 1
            common_links = {link for link, count in common_links_counts.items() if count >= 2}

    # Step 3: Perform Search
    while not container.empty() if algorithm == "bfs" else container:  # while container isn’t empty
        # Step 4: retrieves 1st element from container
        if algorithm == "dfs":
            current_page, path = container.pop()
        elif algorithm == "bfs":
            current_page, path = container.get()
        else:
            current_cost, current_page, path = heapq.heappop(container)

        # Step 5a: If the page has been visited, skip the page
        if current_page in visited:
            continue
        # Step 5b: If the page has not been visited, mark the current page as now visited
        visited.add(current_page)

        # Step 6: Accommodate robustness of broken links in Wikipedia
        try:
            html = internet.get_page(current_page)
        except Exception:
            continue # Skip pages that are broken

        # Step 7: Parse links
        links = Parser.get_links_in_page(html)

        # Step 8: Add unvisited neighbors to the container
        for link in links:
            # if the current link is the goal, return the path
            if link == goal:
                return path + [link]
            # if the link hasn't been visited, add to the queue
            if link not in visited:
                if algorithm == "dfs":
                    container.append((link, path + [link]))
                elif algorithm == "bfs":
                    container.put((link, path + [link]))
                elif algorithm == "dijkstra":
                    new_cost = current_cost + costFn(current_page, link)
                    heapq.heappush(container, (new_cost, link, path + [link]))
                else:
                    priority = 0  # initialize priority
                    # Prioritize links found in the goal page
                    if link in goal_links and link not in common_links:
                        priority -= 1000
                    # Prioritize substrings of goal in link or vise-versa
                    if goal in link or link in goal:
                        priority -= 500
                    if link in common_links:
                        priority += 300

                    # cumulative cost + shorter links preferred + priorities
                    new_cost = current_cost + len(link[6:]) + priority
                    heapq.heappush(container, (new_cost, link, path + [link]))

    # Step 9: If no path exists, return None
    return None

class BFSProblem:
    def __init__(self, internet: Internet):
        self.internet = internet
    # Example in/outputs:
    #  bfs(source = "/wiki/Computer_science", goal = "/wiki/Computer_science") == ["/wiki/Computer_science", "/wiki/Computer_science"]
    #  bfs(source = "/wiki/Computer_science", goal = "/wiki/Computation") == ["/wiki/Computer_science", "/wiki/Computation"]
    # Find more in the test case file.

    # Do not try to make fancy optimizations here. The autograder depends on you following standard BFS and will check all of the pages you download.
    # Links should be inserted into the queue as they are located in the page, and should be obtained using Parser's get_links_in_page.
    # Be very careful not to add things to the "visited" set of pages too early. You must wait for them to come out of the queue first. See if you can figure out why.
    #  This applies for bfs, dfs, and dijkstra's.
    # Download a page with self.internet.get_page().
    def bfs(self, source: str, goal: str):
        return search(self.internet, source, goal, algorithm="bfs")

class DFSProblem:
    def __init__(self, internet: Internet):
        self.internet = internet
    # Links should be inserted into a stack as they are located in the page. Do not add things to the visited list until they are taken out of the stack.
    def dfs(self, source: str, goal: str):
        return search(self.internet, source, goal, algorithm="dfs")

class DijkstrasProblem:
    def __init__(self, internet: Internet):
        self.internet = internet
    # Links should be inserted into the heap as they are located in the page.
    # By default, the cost of going to a link is the length of a particular destination link's name. For instance,
    #  if we consider /wiki/a -> /wiki/ab, then the default cost function will have a value of 8.
    # This cost function is overridable and your implementation will be tested on different cost functions. Use costFn(node1, node2)
    #  to get the cost of a particular edge.
    # You should return the path from source to goal that minimizes the total cost. Assume cost > 0 for all edges.
    def dijkstras(self, source: str, goal: str, costFn = lambda x, y: len(y)):
        return search(self.internet, source, goal, algorithm="dijkstra", costFn = costFn)

class WikiracerProblem:
    def __init__(self, internet: Internet):
        self.internet = internet

    # Time for you to have fun! Using what you know, try to efficiently find the shortest path between two wikipedia pages.
    # Your only goal here is to minimize the total amount of pages downloaded from the Internet, as that is the dominating time-consuming action.

    # Your answer doesn't have to be perfect by any means, but we want to see some creative ideas.
    # One possible starting place is to get the links in `goal`, and then search for any of those from the source page, hoping that those pages lead back to goal.

    # Note: a BFS implementation with no optimizations will not get credit, and it will suck.
    # You may find Internet.get_random() useful, or you may not.

    def wikiracer(self, source: str, goal: str):
        return search(self.internet, source, goal, algorithm="wikiracer")

# KARMA
class FindInPageProblem:
    def __init__(self, internet: Internet):
        self.internet = internet
    # This Karma problem is a little different. In this, we give you a source page, and then ask you to make up some heuristics that will allow you to efficiently
    #  find a page containing all of the words in `query`. Again, optimize for the fewest number of internet downloads, not for the shortest path.

    def find_in_page(self, source = "/wiki/Calvin_Li", query = ["ham", "cheese"]):

        raise NotImplementedError("Karma method find_in_page")

        path = [source]

        # find a path to a page that contains ALL of the words in query in any place within the page
        # path[-1] should be the page that fulfills the query.
        # YOUR CODE HERE

        return path # if no path exists, return None
