import re

import scrapy


class CamaraDiscursosSpider(scrapy.Spider):
    name = "camara_discursos"
    start_url = "https://dadosabertos.camara.leg.br/api/v2/deputados"
    headers = {"Accept": "application/json"}
    discursos_url = "https://dadosabertos.camara.leg.br/api/v2/deputados/{id_parlamentar}/discursos?idLegislatura=56&ordenarPor=dataHoraInicio&ordem=ASC&pagina=1&itens=100"

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, headers=self.headers)

    def parse(self, response):
        # import ipdb; ipdb.set_trace()
        parlamentares = response.json().get("dados")
        for parlamentar in parlamentares:
            yield scrapy.Request(
                url=self.discursos_url.format(id_parlamentar=parlamentar["id"]),
                headers=self.headers,
                callback=self.parse_discurso,
                meta={"identificacao": parlamentar},
            )

    def parse_discurso(self, response):
        # import ipdb; ipdb.set_trace()
        identificacao = response.meta["identificacao"]

        json_response = response.json()
        dados = json_response.get("dados")
        for d in dados:
            d.pop("faseEvento", None)
            yield dict(identificacao, **d)

        links = {l["rel"]: l["href"] for l in json_response.get("links")}

        next_link = links.get("next")
        if next_link:
            yield scrapy.Request(
                url=next_link,
                headers=self.headers,
                callback=self.parse_discurso,
                meta={"identificacao": identificacao},
            )
