import subprocess
import mimetypes
from scrapy import Spider
from scrapy import Request
from scrapy import FormRequest
from scrapy import signals
from scrapy.http import HtmlResponse

class ProjudiSpider(Spider):
    name = 'projudi'
    batch_size = 42
    loot_size = 10000000
    custom_settings = {'DOWNLOAD_DELAY' : .05}


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.offset = 0
        self.ok_requests = 0


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.idle, signal=signals.spider_idle)

        return spider

    def idle(self, spider):
        if self.offset < self.loot_size and self.ok_requests:
            for request in self.request_generator():
                self.crawler.engine.crawl(request, self)


    def start_requests(self):
        yield Request("https://projudi.tjba.jus.br/projudi/PaginaPrincipal.jsp",
                      callback=self.parse_startpage)


    def parse_startpage(self, response):
        captcha_url = response.xpath("id('idImg')/@src").extract_first()

        yield response.follow(captcha_url,
                              callback=self.parse_captcha,
                              meta={'captcha_page': response})


    def parse_captcha(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)

        subprocess.call(["open", "captcha.jpg"])

        answer = input("Digite o captcha, seu lindo!: ")

        captcha_page = response.meta['captcha_page']

        yield FormRequest.from_response(
            captcha_page,
            "formConsultaPublica",
            formdata={'captcha': answer, 'numeroProcesso':'1'},
            callback=self.parse_captcha_result)


    def parse_captcha_result(self, response):
        return self.request_generator()


    def request_generator(self):
        self.ok_requests = 0

        url = 'https://projudi.tjba.jus.br/projudi/listagens/DownloadArquivo?arquivo=%d'

        for i in range(self.offset, self.offset + self.batch_size):
            yield Request(url % i, meta={'id' : i})

        self.offset += self.batch_size


    def parse(self, response):
        self.ok_requests += 1

        if isinstance(response, HtmlResponse):
            title = response.xpath('//title/text()').extract_first()
            if title == 'Error Page':
                return

            title = response.css('p.tituloPagina::text').extract_first()
            if title == 'Download do arquivo não permitido':
                return

        ext = mimetypes.guess_extension(
            response.headers['Content-Type'].split(b';')[0].decode())

        if ext == '.htm':
            ext = '.html'

        with open('loot/%06d%s' % (response.meta['id'], ext), 'wb') as f:
            f.write(response.body)
