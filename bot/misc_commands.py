import struct

from pnglatex import pnglatex


def echo(room, event, payload):
    if payload:
        room.send_text(' '.join(payload))
    else:
        room.send_text('Please enter something to echo')


def latex(room, event, payload):
    try:
        path = pnglatex(' '.join(payload))
    except ValueError as e:
        room.send_text(str(e))
    else:
        with path.open('rb') as img:
            data = img.read()
            size = len(data)
            if size >= 24 and data.startswith(b'\211PNG\r\n\032\n') and (data[12:16] == b'IHDR'):
                w, h = struct.unpack(">LL", data[16:24])
            else:
                w, h = struct.unpack(">LL", data[8:16])
            width = int(w)
            height = int(h)
            url = room.client.api.media_upload(data, 'image/png')['content_uri']
        name = path.name
        path.unlink()
        room.send_image(
            url, name, mimetype='image/png', h=height, w=width, size=size
        )