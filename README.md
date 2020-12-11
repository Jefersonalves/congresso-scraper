## congresso-scraper

Scraping das proposições/materias e discursos do congresso usando o scrapy

## como executar

Para executar o spider `camara_discursos` e salvar os itens em um arquivo csv:
>```sh
>scrapy crawl camara_discursos -o discursos.csv
>```

## spiders disponíveis
* camara_discursos
* camara_proposicoes
* senado_discursos
* senado_materias

## to do
* transformar data de inicio e data fim em parametros para os spiders, atualmente está hardcoded nos spiders camara_proposicoes e senado_materias
* usar a configuração de header do scrapy