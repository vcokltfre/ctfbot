import re

flag = re.compile(r"Elem{[a-zA-Z0-9]{18}}")

def paginate(lines_in: list, maxlen: int = 2000, lang=''):
    lines = []
    for line in lines_in:
        for match in flag.findall(line):
            print(match)
            line = line.replace(match, "Elem{" + 'X' * 18 + "}")
        lines.append(line)
    pages = []

    current_page = [];
    current_length = 0;

    for line in lines:
        if len(line) + 1 + 7 + len(lang) > maxlen:
            line = line[:(maxlen - 1 - 7 - len(lang))]
        if not current_page:
            current_page.append(f"```{lang}")
            current_length += 7 + len(lang)
        if len(line) + 1 + current_length <= maxlen:
            current_page.append(line)
            current_length += len(line) + 1
        else:
            current_page.append("```")
            pages.append(current_page)
            current_page = [f"```{lang}", line]
            current_length = len(lang) + 7 + len(line) + 1

    current_page.append("```")
    pages.append(current_page)

    text_pages = ["\n".join(ps) for ps in [page for page in pages]]
    return text_pages
