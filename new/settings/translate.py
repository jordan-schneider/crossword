def string(node):
    return node.text.strip()


def integer(node):
    return int(node.text.strip())


def decimal(node):
    return int(node.text.strip())


def font(node):
    return string(node[0]), integer(node[1])


def choice(node):
    return [string(child) for child in node.getchildren()][integer(node)]


mapping = {
    "string": string,
    "color": string,
    "integer": integer,
    "natural": integer,
    "decimal": decimal,
    "font": font,
    "choice": choice,
    "ip": string,
    "port": integer,
}


def cast(node):
    translation = mapping.get(node.get("type"), string)
    return translation(node)
