def application(environ, start_response):
    status = '200 OK'
    output = b'Headers received:\n\n'

    for key, value in sorted(environ.items()):
        if key.startswith('HTTP_'):
            output += bytes('{}: {}\n'.format(key, value), 'utf-8')

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]