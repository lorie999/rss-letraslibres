import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import time

SECCIONS = [
    {
        "url": "https://letraslibres.com/seccion/literatura/",
        "titol": "Letras Libres - Literatura",
        "fitxer": "letraslibres_literatura.rss"
    },
    {
        "url": "https://letraslibres.com/seccion/libros/",
        "titol": "Letras Libres - Libros",
        "fitxer": "letraslibres_libros.rss"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for seccio in SECCIONS:
    print(f"\nProcessant: {seccio['titol']}")
    resposta = requests.get(seccio["url"], headers=HEADERS)

    if resposta.status_code != 200:
        print(f"Error: codi {resposta.status_code}")
        continue

    sopa = BeautifulSoup(resposta.text, "html.parser")

    fg = FeedGenerator()
    fg.title(seccio["titol"])
    fg.link(href=seccio["url"])
    fg.description(seccio["titol"])

    articles = sopa.find_all("article")
    print(f"Trobats {len(articles)} articles")

    for article in articles:
        titol_tag = article.find("h2") or article.find("h3")
        link_tag = article.find("a", href=True)
        img_tag = article.find("img")

        if not titol_tag or not link_tag:
            continue

        titol = titol_tag.get_text(strip=True)
        link = link_tag["href"]
        if link.startswith("/"):
            link = "https://letraslibres.com" + link

        imatge = ""
        if img_tag:
            imatge = img_tag.get("src", "") or img_tag.get("data-src", "")

        subtitol = ""
        try:
            resposta_article = requests.get(link, headers=HEADERS)
            sopa_article = BeautifulSoup(resposta_article.text, "html.parser")
            subtitol_tag = sopa_article.find("div", class_="cs-entry__subtitle")
            if subtitol_tag:
                subtitol = subtitol_tag.get_text(strip=True)
            time.sleep(1)
        except Exception:
            pass

        if imatge:
            contingut = f'<img src="{imatge}" /><p>{subtitol}</p>'
        else:
            contingut = f'<p>{subtitol}</p>' if subtitol else f'<p>{titol}</p>'

        fe = fg.add_entry()
        fe.title(titol)
        fe.link(href=link)
        fe.description(subtitol if subtitol else titol)
        fe.content(contingut, type="html")
        print(f"  -> {titol[:60]}...")

    fg.rss_file(seccio["fitxer"])
    print(f"Feed guardat com a {seccio['fitxer']}")