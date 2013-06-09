PstatsInteractive
=================

PstatsInteractive is a mini python web service for viewing python profiles.
The goal of this project is to create an interactive profile inspector that works
with very large profiles.

There are already a few ways to view python profiles, but each has it's own
limitations or shortcomings.

* Interactively with `ipython` using the `pstats` module

  This is standard method for viewing profiles. It works with profiles of any size
  but it can take a while to find exactly what you're looking for. It's missing
  nice visuals, and a way to tag and share interesting views.

* [RunSnakeRun](http://www.vrplumber.com/programming/runsnakerun/)

  Includes a nice visual view of calls, but it can be hard to fit all the data in
  a single screen.  Large profiles end up looking like many thin layers of an
  onion. Also lacks a way to tag and share interesting views.

* [gprofdof](http://code.google.com/p/jrfonseca/wiki/Gprof2Dot) and [Graphviz](http://www.graphviz.org/) to create an image

  Static image works well for smaller profiles, but can be difficult to navigate
  large profiles. Easy to share the entire image, but not a sub-section. Not
  interactive.

* [snakeviz](http://jiffyclub.github.io/snakeviz/) which is a web app and d3 graph

  Does not work with large profiles.

* [pstats_viewer.py](http://chadaustin.me/2008/05/open-sourced-our-pstats-viewer/) a single python file that starts a basic web server

  This is a step in right direction. Lacks styling and a visual representation.
  The work is done on the server side, so not as interactive as it could be.

Plan
----

* reuse elements of `pstats_viewer.py` and `snakeviz` to create a client-side web based viewer
* use [dagre](https://github.com/cpettitt/dagre) to create graphviz like diagrams of sub-sections of a profile
* use [d3js](http://d3js.org/) to create pie charts of callee time (including gc time)
* web server should serve json blobs of profiles
* include a page to allow selection of available profiles


Notes
-----

Pstats are stored using this structure. Primitive call count is the number of
non-recursive calls.


    { 
        (
            file_name,
            line_number,
            function_name,
        ): (
            primitive call count,
            total call count,
            total time,
            cumulative time,
            callers
        ),
        ...
    }

callers is a dict with this structure:

    {
        (
            file_name, 
            line_number, 
            function_name
        ): (
            total call count,
            primitive call count,
            total time attributed to this caller,
            cumulative time attributed to this caller
        ),
        ...
    }


