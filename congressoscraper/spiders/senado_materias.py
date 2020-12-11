import scrapy


class SenadoMateriasSpider(scrapy.Spider):
    name = "senado_materias"
    start_url = "http://legis.senado.leg.br/dadosabertos/materia/pesquisa/lista?dataFimApresentacao={data_fim}&dataInicioApresentacao={data_inicio}"
    relatoria_url = (
        "http://legis.senado.leg.br/dadosabertos/materia/relatorias/{cod_materia}"
    )
    headers = {"Accept": "application/json"}

    def start_requests(self):
        data_inicio = "20150101"  # "20150101"
        data_fim = "20151231"
        yield scrapy.Request(
            url=self.start_url.format(data_fim=data_fim, data_inicio=data_inicio),
            headers=self.headers,
        )

    def parse(self, response):
        materia_list = (
            response.json().get("PesquisaBasicaMateria").get("Materias").get("Materia")
        )
        for m in materia_list:
            identificacao = m.get("IdentificacaoMateria")
            cod_materia = identificacao.get("CodigoMateria")
            ementa = m.get("DadosBasicosMateria").get("EmentaMateria")
            autoria_master = m.get("AutoresPrincipais")

            autores = []
            if autoria_master:
                autoria = autoria_master.get("AutorPrincipal")
                if type(autoria) != list:
                    nome_parlamentar = autoria.get("NomeAutor")
                    codigo_parlamentar = autoria.get(
                        "IdentificacaoParlamentar", {"CodigoParlamentar": None}
                    ).get("CodigoParlamentar")
                    autores.append((nome_parlamentar, codigo_parlamentar))
                else:
                    for autor in autoria:
                        nome_parlamentar = autor.get("NomeAutor")
                        codigo_parlamentar = autor.get(
                            "IdentificacaoParlamentar", {"CodigoParlamentar": None}
                        ).get("CodigoParlamentar")
                        autores.append((nome_parlamentar, codigo_parlamentar))

            data = dict(
                identificacao, **{"EmentaMateria": ementa}, **{"Autores": autores}
            )

            yield scrapy.Request(
                url=self.relatoria_url.format(cod_materia=cod_materia),
                headers=self.headers,
                callback=self.parse_relatoria,
                meta={"materia": data},
            )

    def parse_relatoria(self, response):
        # import ipdb; ipdb.set_trace()
        materia = response.meta["materia"]
        relatoria = (
            response.json().get("RelatoriaMateria").get("Materia").get("RelatoriaAtual")
        )

        relatores = []

        if relatoria:
            relatores_lista = relatoria.get("Relator")
            for relator in relatores_lista:
                identificacao = relator.get("IdentificacaoParlamentar")
                relatores.append(
                    (
                        identificacao.get("NomeParlamentar"),
                        identificacao.get("CodigoParlamentar"),
                    )
                )

        yield dict(materia, **{"Relatores": relatores})
