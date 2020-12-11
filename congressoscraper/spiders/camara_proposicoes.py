import scrapy


class CamaraProposicoesSpider(scrapy.Spider):
    name = "camara_proposicoes"
    start_url = "https://dadosabertos.camara.leg.br/api/v2/proposicoes?dataApresentacaoInicio={data_inicio}&dataApresentacaoFim={data_fim}&siglaTipo=PEC&siglaTipo=PLP&siglaTipo=PL&siglaTipo=MPV&itens=100&ordem=ASC&ordenarPor=id"
    headers = {"Accept": "application/json"}
    parlamentares = {}
    autores_url = (
        "https://dadosabertos.camara.leg.br/api/v2/proposicoes/{cod_proposicao}/autores"
    )

    def start_requests(self):
        data_inicio = "2015-01-01"
        data_fim = "2019-12-31"
        yield scrapy.Request(
            url=self.start_url.format(data_fim=data_fim, data_inicio=data_inicio),
            headers=self.headers,
        )

    def parse(self, response):
        # import ipdb; ipdb.set_trace()
        proposicoes = response.json().get("dados")
        for prop in proposicoes:
            yield scrapy.Request(
                url=prop.get("uri"),
                headers=self.headers,
                callback=self.parse_proposicao,
            )

        links = {l["rel"]: l["href"] for l in response.json().get("links")}
        next_link = links.get("next")
        if next_link:
            yield scrapy.Request(
                url=next_link, headers=self.headers, callback=self.parse
            )

    def parse_proposicao(self, response):
        # import ipdb; ipdb.set_trace()
        prop = response.json().get("dados")
        prop_status = prop.get("statusProposicao")
        prop.pop("statusProposicao", None)

        prop_data = dict(prop, **prop_status)
        # autores_url = prop.get('uriAutores')

        cod_proposicao = prop.get("id")
        yield scrapy.Request(
            url=self.autores_url.format(cod_proposicao=cod_proposicao),
            headers=self.headers,
            callback=self.parse_autores,
            meta={"prop": prop_data},
        )

    def parse_autores(self, response):
        # import ipdb; ipdb.set_trace()
        autores = response.json().get("dados")
        autores_data = [(a["nome"], a["uri"]) for a in autores]
        prop_data = response.meta["prop"]

        yield dict(prop_data, **{"autores": autores_data})
