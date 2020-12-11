import re

import scrapy


class SenadoDiscursosSpider(scrapy.Spider):
    name = "senado_discursos"
    start_url = "http://legis.senado.leg.br/dadosabertos/senador/lista/atual"
    discursos_url = (
        "http://legis.senado.leg.br/dadosabertos/senador/{codigo_arlamentar}/discursos"
    )
    headers = {"Accept": "application/json"}

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, headers=self.headers)

    def parse(self, response):
        # import ipdb; ipdb.set_trace()
        parlamentares = (
            response.json()
            .get("ListaParlamentarEmExercicio")
            .get("Parlamentares")
            .get("Parlamentar")
        )
        for parlamentar in parlamentares:
            identificacao = parlamentar.get("IdentificacaoParlamentar")
            identificacao.pop("Telefones", None)
            codigo_arlamentar = identificacao.get("CodigoParlamentar")
            yield scrapy.Request(
                url=self.discursos_url.format(codigo_arlamentar=codigo_arlamentar),
                headers=self.headers,
                callback=self.parse_discurso,
                meta={"identificacao": identificacao},
            )

    def parse_discurso(self, response):
        parlamentar = response.json().get("DiscursosParlamentar").get("Parlamentar")
        if parlamentar:
            pronunciamentos = parlamentar.get("Pronunciamentos").get("Pronunciamento")
            for p in pronunciamentos:
                url_texto = p.get("UrlTexto")
                discurso_data = {
                    "CodigoPronunciamento": p.get("CodigoPronunciamento"),
                    "DataPronunciamento": p.get("DataPronunciamento"),
                    "SiglaPartidoParlamentarNaData": p.get(
                        "SiglaPartidoParlamentarNaData"
                    ),
                    "UfParlamentarNaData": p.get("UfParlamentarNaData"),
                    "NomeCasaPronunciamento": p.get("NomeCasaPronunciamento"),
                    "TextoResumo": p.get("TextoResumo"),
                    "UrlTexto": url_texto,
                    "TipoUsoPalavra": p.get("TipoUsoPalavra").get("Descricao"),
                }
                meta = dict(response.meta["identificacao"], **discurso_data)
                if url_texto:
                    yield scrapy.Request(
                        url=url_texto, callback=self.parse_page, meta={"discurso": meta}
                    )

    def parse_page(self, response):
        # import ipdb; ipdb.set_trace()
        text_list = response.css(".texto-integral *::text").getall()
        text = " ".join(text_list)
        text = re.sub(r"\xa0\xa0\xa0\xa0", " ", text)
        text = re.sub(r"[ ]+", " ", text).strip()

        discurso = response.meta["discurso"]
        yield dict(discurso, **{"text": text})
