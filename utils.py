

def is_valid_ipv4(address):
    """IPv4 address validator"""

    if address.count('.') != 3:
        return False

    for i in address.split('.'):
        if not i or not 0 <= int(i) < 256:
            return False

    return True


def htmlify(matrix, head=True):
    with open('template.html', 'r') as template:
        html = template.read()

    html = html.replace('{{table}}', tablify(matrix, head))
    return html


def tablify(matrix, head=True):
    table = '<table id="Table">\n'

    for row in matrix:
        tr = '\t<tr>\n'

        for col in row:
            if head:
                head = False
                td = '\t\t<th> {} </th>\n'.format(col)
            else:
                td = '\t\t<td> {} </td>\n'.format(col)
            tr += td

        tr += '\t<tr>\n'
        table += tr

    table += '</table>'
    return table

if __name__ == '__main__':
    content = [
        ('Unique IP Count', 420),
        ('Unique Content Count', 0),
        ('The user who watched the most content', '192.240.109.106'),
        ('Most viewed content', '-'),
    ]

    with open('output.html', 'w') as stream:
        stream.write(htmlify(content, head=False))
