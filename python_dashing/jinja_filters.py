jinja_filters = {}

def a_filter(func):
    jinja_filters[func.__name__] = func
    return func

@a_filter
def sparkline(data, w=100.0, h=30.0, c="white"):
    data = [int(d) for d in data]

    header = '<svg width="{0}" height="{1}"><g style="fill-opacity:1.0; stroke:{2}; stroke-width:1;">'
    lines = [header.format(w, h, c)]

    data_min = min(data)
    data_max = max(data)
    data_spread = data_max - data_min if data_max != data_min else 1
    scaled_data = list(map(lambda d: h - ((d - data_min) / data_spread * h), data))
    w_point = w / len(data)

    line = lambda **kwargs: '  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />'.format(**kwargs)
    for i in range(len(data)-1):
        lines.append(line(x1=i*w_point, y1=scaled_data[i], x2=(i+1)*w_point, y2=scaled_data[i+1]))

    lines.append("</g></svg>")
    return '\n'.join(lines)
