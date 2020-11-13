def paginate(lines: list, maxlen: int = 2000):
    pages = []
    page = [[], 0]

    for line in lines:
        if not page[0]:
            page[0].append("```yml")
            page[1] += 11
        if len(line) + 1 + page[1] <= maxlen:
            page[0].append(line)
            page[1] += len(line) + 1
        else:
            page[0].append("```")
            pages.append(page[0])
            page = [[], 0]
    if page[0]:
        page[0].append("```")
        pages.append(page[0])

    text_pages = ["\n".join(ps) for ps in [page for page in pages]]
    return text_pages
