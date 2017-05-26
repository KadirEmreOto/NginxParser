# -*- coding: UTF-8 -*-
import os
import argparse

from utils import htmlify
from collections import Counter


class Parser(object):
    def __init__(self):
        self.conf = [  # log configuration (ordered)
            ('ip', "  "),  # -> (attribute_name, 'begin + end')
            ('time', '[]'),
            ('method', '""'),
            ('http_status', '  '),
            ('filesize', '  '),
            ('filename', '""'),
            ('user-agent', '""'),
            (None, '""'),  # the name of attribute not determined yet
            ('rt', '  '),  # rt=XXX        "rt=" part should be removed at func parse_line
            ('ut', '""'),
            ('cs', '  '),  # cs=HIT|MISS   "cs=" part should be removed at func parse_line
        ]

    def configure(self, fields=None, conf=None):
        """
        change the default configuration for different log files

        Arguments:
            * fields parameter should be used for just changing the order of self.conf. It means all attribute which are
                set as default must be in the "fields".
                fields is a list of attribute names

            * configuration list (self.conf) can be overridden with conf parameter.
                conf parameter should be a list of tuples which contain attribute name and deliminators.

        Example:
            self.configure(fields=['time', 'ip', 'method', 'user-agent'])   # ValueError will be raised.

            self.configure(fields=['time', 'ip', 'method', 'user-agent', 'http_status', 'filesize', None, 'rt' 'ut', 'cs']) # valid usage
            self.configure(conf=[('ip', "  "), ('time', '[]'), ('http_status', '  '), ('cs', '  ')]) # valid usage
        """

        if fields:
            self.conf.sort(key=lambda item: fields.index(item[0]))

        elif conf:
            self.conf = conf

    @classmethod
    def parse_method(cls, method):
        flag = method.count('(') == 2

        if not flag:
            yield False

        else:
            yield method[: method.find(' ')]

            start = method.find('/')
            start = method.find('/', start+1)
            start = method.find('/', start+1)
            end = method.find('/', start+1)
            yield method[start+1: end]

            start = method.find('(', end)
            end = method.find(')', start)
            yield (method[start + 1: end-5] + '0' * 5).lstrip('0')

            start = method.find('(', end)
            end = method.find('=', start)
            yield method[start + 1: end]

    def parse_line(self, line, fields=None, ignore=None):
        length = len(line)
        precursor = 0

        for attr, sep in self.conf:
            while precursor != 0 and precursor < length and line[precursor] != sep[0]:
                precursor += 1

            successor = precursor + 1

            while successor < length and line[successor] != sep[1]:
                successor += 1

            if (ignore is None or attr not in ignore) and (fields is None or attr in fields):
                if attr == 'rt' or attr == 'cs':  # not a good programming, can be generalized
                    precursor += 4

                yield line[precursor:successor + 1].strip(' "')  # creates a "generator" for speeding-up the process

            precursor = successor
            if sep[1] == '"':
                precursor += 1

    def parse_file(self, path, output_type='text', output_file='output.txt', ignore=None):
        if not os.path.exists(path):
            return False

        counter = {item[0]: Counter() for item in self.conf}
        counter.update({item: Counter() for item in ['content', 'bitrate', 'type', 'browser']})

        with open(path, 'r') as log:
            for line in log:
                parsed_line = self.parse_line(line, ignore=ignore)

                for index, item in enumerate(self.conf):
                    if item[0] not in ignore:
                        if item[0] == 'http_status':
                            status = parsed_line.next()

                            if status[0] != '4':  # why 4 is important ? 
                                status = status[0] + 'xx'

                            counter['http_status'][status] += 1

                        elif item[0] == 'user-agent':
                            user_agent = parsed_line.next().strip()

                            if user_agent == '-':
                                continue

                            end = user_agent.find(' ')

                            browser = user_agent[:end]
                            if browser:
                                counter['browser'][browser] += 1

                        elif item[0] == 'method':
                            parsed_method = self.parse_method(parsed_line.next())

                            if not parsed_method.next():
                                continue

                            counter['content'][parsed_method.next()] += 1
                            counter['bitrate'][parsed_method.next()] += 1
                            counter['type'][parsed_method.next()] += 1

                        else:
                            counter[self.conf[index][0]][parsed_line.next()] += 1

        del counter['bitrate']['']

        top1_user = counter.get('ip', Counter()).most_common(1)
        top1_user = top1_user[0][0] if top1_user else '-'

        top1_content = counter.get('content', Counter()).most_common(1)
        top1_content = top1_content[0][0] if top1_content else '-'

        s = float(sum(counter['bitrate'].values()))
        bitrate = ', '.join(map(lambda item: '{} = %{:.2f}'.format(item[0], item[1]/s*100),
                                counter['bitrate'].most_common(5)))

        s = float(sum(counter['http_status'].values()))
        http_status = ', '.join(map(lambda item: '{} = %{:.2f}'.format(item[0], item[1]/s*100),
                                counter['http_status'].most_common(5)))

        s = float(sum(counter['browser'].values()))
        browser = ', '.join(map(lambda item: '{} = %{:.2f}'.format(item[0], item[1]/s*100),
                                counter['browser'].most_common(5)))

        output = ''

        if output_type == 'text':
            output += 'Unique IP Count: {} \n'.format(len(counter.get('ip', [])))
            output += 'Unique Content Count: {} \n'.format(len(counter.get('content', [])))
            output += 'The user who watched the most content: {} \n'.format(top1_user)
            output += 'Most viewed content: {} \n'.format(top1_content)
            output += 'Bitrates: {} \n'.format(bitrate)
            output += 'Browser Usage Rates: {} \n'.format(browser)
            output += 'HTTP Status Rates: {} \n'.format(http_status)
            for type_, count in counter['type'].most_common():
                output += '{} Count: {} \n'.format(type_.capitalize(), count)

        elif output_type == 'html':
            table = [
                ('Unique IP Count', len(counter.get('ip', []))),
                ('Unique Content Count', len(counter.get('content', []))),
                ('The user who watched the most content', top1_user),
                ('Most viewed content', top1_content),
                ('Bitrates', '{} \n'.format(bitrate.replace(', ', ' <BR>\n'))),
                ('Browser Usage Rates', '{} \n'.format(browser.replace(', ', ' <BR>\n'))),
                ('HTTP Status Rates', '{} \n'.format(http_status.replace(', ', ' <BR>\n'))),
            ]

            for type_, count in counter['type'].most_common():
                table.append(('{} Count'.format(type_.capitalize()), count))

            output = htmlify(table, head=False)

        if output_file == 'stdout':
            print output

        else:
            with open(output_file, 'w') as stream:
                stream.write(output)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Nginx Access Log Parser")

    ap.add_argument('-i', '--input_file', required=True)
    ap.add_argument('-o', '--output_file', default='stdout')
    ap.add_argument('-t', '--output_type', default='text')

    opts = ap.parse_args()

    parser = Parser()
    parser.parse_file(opts.input_file, ignore={'rt', 'ut', 'cs', 'time', None},
                      output_file=opts.output_file, output_type=opts.output_type)
