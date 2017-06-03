# NginxParser
NginxParser is an open source project that parses and analyzes nginx access log files. The project was written with python programming language, therefore it can be executed with pypy for speed-up the process.

## Example Usage
    usage: parser.py [-h] -i INPUT_FILE [-o OUTPUT_FILE] [-t {text,html}]

    $ pypy parser.py -h
    $ pypy parser.py -i nginx.access.log
    $ pypy parser.py -i nginx.access.log -o output.txt -t text
    $ pypy parser.py --input-file=nginx.access.log --output-file=output.html --output-type=html

    $ python
    >>> from parser import Parser
    >>> parser = Parser()
    >>> parser.parse_file('nginx.access.log', output_file='result.txt', output_type='text')


## Example Output
![alt text](http://i.imgur.com/pabGAbs.png)
