#!/usr/bin/env python

from __future__ import print_function
from collections import OrderedDict
import json
import os
import re
import sys

LEVEL = {
    'OK': 'test_ok',
    'FAIL': 'test_fail',
    'ERROR': 'test_error',
    'SKIP': 'test_skip'
}

def header():
    return """<!DOCTYPE html>
<html>
<head>
<title>Page Title</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/chartist.js/latest/chartist.min.css">
<script src="https://cdn.jsdelivr.net/chartist.js/latest/chartist.min.js"></script>
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js"></script>
<style>
.test_ok    { color: green; fill: green; stroke: green;}
.test_error { color: red; fill: red; stroke: red;}
.test_fail  { color: darkred; fill: darkred; stroke: red;}
.test_skip  { color: gray; fill: gray; stroke; gray}
.mono       { font-family: monospace; }
ul          { list-style: none; padding: 0px; }
a           { color: inherit; text-decoration:none; cursor: pointer; }
body        { font-size: 0.8em; }
.ct-label   { font-size: 1.2em; color: white; fill: white; }
.log        { font-family: monospace; }
.hidden     { display: none; }
.float      { float: left; }
.center     { text-align: center; }
</style>
</head>
<body>"""

def footer():
    return """
<script>
(function() {
    $('a[data-res]').bind('click', function (elem) {
        $('#' + elem.target.dataset.res).toggle();
    });
})();
</script>
</body></html>
"""

class Result2Html(object):

    def __init__(self, logfile):
        self.name = "generic"
        self.count = OrderedDict(zip(LEVEL, (0,) * len(LEVEL)))
        self.html = []
        self.log = logfile


    def compute(self):
        pass

    def render(self):
        series = []
        for entry, val in self.count.items():
            if val == 0:
                continue
            series.append({
                'value': val,
                'className': 'test_%s' % entry.lower()
            })

        piechart = """
        <div>
        <div>
        <table>
        <tr><td class='center'><h1>""" + self.name + """</h1>
                <p><a data-res='""" + self.name + """_res'>Show/Hide</a></p>
                <p><a href='""" + self.name + """'>Logs</p>
             </td>
             <td>
        <div id='chart_""" + self.name + """' class='ct-chart ct-perfect-fourth' style='width: 300px;'></div>
             </td>
             <td><ul>""" + "".join(["<li>{0}: {1}</li>".format(k,v ) for k,v in self.count.items()]) + """</ul>
             </td>
        </tr>
        </table>
        </div>
        <script>
        (function () {
        var data = { series:""" + json.dumps(series, indent=4) + """, };

        var sum = function(a, b) { return (a.value ? a.value : a) + b.value; };

        new Chartist.Pie('#chart_""" + self.name + """', data, {
          labelInterpolationFnc: function(value) {
            return Math.round(value / data.series.reduce(sum) * 100) + '%';
          }
        })
        })();
        </script>"""
        output = piechart #

        output += "<div id='{name}_res' class='hidden'>".format(name=self.name)
        output += "<ul>"
        output += "\n".join(self.html)
        output += "</ul>"
        output += "<hr/>"
        # output += self.include_file("res", self.log)
        output += "</div>"

        output += "</div>"
        return output

    def include_file(self, tag, log):
        output = "<div id='log_{name}_{tag}' class='log hidden'>".format(
            name=self.name, tag=tag)
        curline = 0
        res = []
        with open(log) as f_in:
            for line in f_in:
                curline += 1
                res.append("<a name='{name}_{tag}_{curline}'>{line}</a>\n".format(
                    name=self.name, tag=tag, line=line, curline=curline))
        output += "<br/>".join(res)
        output += "</div>"
        return output


    def colorize(self, line, level, href):
        self.html.append("<li class='{color}' data-href='{name}_res_{href}'>{line}</li>".format(
            color=LEVEL[level], href=href, name=self.name, line=line))
        self.count[level] += 1

class S3Ceph(Result2Html):
    def __init__(self, *args, **kwargs):
        super(S3Ceph, self).__init__(*args, **kwargs)
        self.name = "s3ceph"

    def compute(self):
        curline = 0
        with open(self.log) as f_in:
            for line in f_in:
                curline += 1
                line = line.strip('\n')
                word = line.split(' ')[-1].upper()
                if word not in LEVEL:
                    continue
                self.colorize(line, word, href=curline)

class S3Cmd(Result2Html):
    def __init__(self, *args, **kwargs):
        super(S3Cmd, self).__init__(*args, **kwargs)
        self.name = "s3cmd"
        self.ansi_escape = re.compile(r'\x1b[^m]*m')

    def compute(self):
        curline = 0
        with open(self.log) as f_in:
            for line in f_in:
                curline += 1
                line = line.strip('\n')
                line = self.ansi_escape.sub('', line)
                word = line.split(' ')[-1].upper()
                if 'FAIL' in line: # should be a regex
                    word = 'FAIL'
                if word not in LEVEL:
                    continue
                self.colorize(line, word, href=curline)


ANALYSE = {
    "s3ceph": S3Ceph,
    "s3cmd": S3Cmd,
}

def create_html_report(report):
    out = open(os.path.join(report, "index.html"), "w")
    out.write(header())

    items = os.listdir(report)
    summary = {}
    for entry in items:
        path = os.path.join(report, entry)
        if not os.path.isdir(path):
            continue
        log = os.path.join(path, "test_" + entry + ".log")
        if not os.path.isfile(log):
            print("Missing result file")
            continue

        cls = ANALYSE[entry](logfile=log)
        cls.compute()
        summary[entry] = cls.count
        out.write(cls.render())
    out.write(footer())
    out.close()

    # dump number of test ok/fails/... per testsuite
    out = open(os.path.join(report, "summary.json"), "w")
    json.dump(summary, out, indent=4)
    out.close()

if __name__ == "__main__":
    create_html_report(os.path.abspath(sys.argv[1]))
