import scrapy


# Aquí aparecen todos las expresiones xpath
# Titulo = //h1/a/text()
# Quotes = //div[@class="col-md-8"]/div/span[@class="text"]/text()
# Authors = //small[@class="author"]/text()
# Top ten tags = //div[contains(@class,"tags-box")]//span[@class="tag-item"]/a/text()
# Next page button = //li[@class="next"]/a/@href

class QuotesSpider(scrapy.Spider):
    name = 'quotes' # Nombre
    start_urls = [
        'http://quotes.toscrape.com/'
    ]  # URL a hacer scrap

    custom_settings = {
        'FEED_URI': 'quotes.json',
        'FEED_FORMAT': 'json',
        'CONCURRENT_REQUESTS': 24,
        'MEMUSAGE_LIMIT_MB': 2048,
        'ROBOTSTXT_OBEY': True,
        'FEED_EXPORT_ENCODING': 'utf-8'
    }


    def parse_only_quotes_authors(self, response, **kwargs): # Método cuando se abre una nueva página

        if kwargs:  # Se agregan las citas y autores que se han ido recogiendo
            quotes = kwargs['quotes'] 
            authors = kwargs['authors']

        quotes.extend(response.xpath('//div[@class="col-md-8"]/div/span[@class="text"]/text()').getall()) # Agregamos las citas de la nueva página
        authors.extend(response.xpath('//small[@class="author"]/text()').getall()) # Agregamos los autores de la nueva página
        
        
        next_page_button_link = response.xpath('//li[@class="next"]/a/@href').get() # Link del botón

        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes_authors, cb_kwargs={'quotes':quotes, 'authors':authors}) # Recursividad

        else:
            yield {
                'wholequote': list(zip(authors,quotes)) # Escribe en el documento el autor y la cita 
            }
    

    def parse(self, response):
        tittle = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//div[@class="col-md-8"]/div/span[@class="text"]/text()').getall()
        top_tags = response.xpath('//div[contains(@class,"tags-box")]//span[@class="tag-item"]/a/text()').getall()
        authors = response.xpath('//small[@class="author"]/text()').getall()

        top = getattr(self, 'top', None) # Para poder especificar en consola cuantos top_tags queremos
        if top:
            top = int(top)
            top_tags = top_tags[:top]
            

        yield {
            'tittle': tittle,
            'top_tags': top_tags
        } # Se escribe el titulo de la página y la cantidad de tags que especificamos, si no se especificó, aparecen 10

        next_page_button_link = response.xpath('//li[@class="next"]/a/@href').get() # Link del botón

        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes_authors, cb_kwargs={'quotes':quotes, 'authors':authors})
            # Al existir una nueva página, usamos el método parse_only_quotes_authors para abrirla
    