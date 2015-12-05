def string(node):
    print(node, node.text)
    return node.text.strip()


def integer(node):
    return int(node.text.strip())


def decimal(node):
    return float(node.text.strip())


def font(node):
    return node[0].text.strip(), int(node[1].text.strip())


def choice(node):
    return [child.text.strip() for child in node.getchildren()][int(node.text.strip())]

color = string
natural = integer

lookup = {
    "string": string,
    "integer": integer,
    "decimal": decimal,
    "font": font,
    "choice": choice,
    "color": color,
    "natural": natural
}


def cast(node):
    function = lookup.get(node.get("type"), string)
    return function(node)
