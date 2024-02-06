from copy import copy
from typing import Any

from src.schemas.books import BookAPISchema
from config.gb_api import gb_api_settings
from src.utils.logger import logger

from .abstract import AbstractBooksAPI
from ..client import AioHTTPSessionClient


class GoogleBooksAPI(AbstractBooksAPI):
    session_client = AioHTTPSessionClient(
        gb_api_settings.BASE_URL + gb_api_settings.API_VERSION + '/volumes'
    )
    result_fields_params = {
        "fields": "id,volumeInfo(title,subtitle,authors,publishedDate,description,"
                  "industryIdentifiers,categories,language)"
    }
    results_fields_params = {
        "fields": f"items({result_fields_params['fields']})"
    }

    @classmethod
    async def get_by_id(cls, id: str) -> BookAPISchema:
        status, data = await cls.session_client.get(f"/{id}", params=cls.result_fields_params)
        logger.info(data)
        return BookAPISchema(
                gb_id=data['id'],
                ISBN=cls.getISBNIfExists(data['volumeInfo'].get('industryIdentifiers')),
                title=data['volumeInfo'].get('title'),
                subtitle=data['volumeInfo'].get('subtitle'),
                description=data['volumeInfo'].get('description'),
                language=data['volumeInfo'].get('language'),
                pub_date=data['volumeInfo'].get('publishedDate'),
                categories=', '.join(data['volumeInfo'].get('categories'))
                if data['volumeInfo'].get('categories') is not None else None,
                authors=', '.join(data['volumeInfo'].get('authors'))
                if data['volumeInfo'].get('authors') is not None else None
            )

    @classmethod
    async def search(cls,
                     gb_id: str | None,
                     query: str | None,
                     intitle: str | None,
                     inauthor: str | None,
                     isbn: str | None,
                     categories: str | None
                     ) -> list[BookAPISchema]:
        params = copy(cls.results_fields_params)
        if gb_id:
            params['q'] = gb_id
        else:
            params['q'] = query or ''
        if intitle:
            params['q'] += '+intitle:' + intitle
        if inauthor:
            params['q'] += '+inauthor' + inauthor
        if isbn:
            params['q'] += '+isbn' + isbn
        if categories:
            params['q'] += '+subject' + ','.join(categories)
        status, res = await cls.session_client.get('', params=params)
        logger.info(res)
        return [
            BookAPISchema(
                gb_id=data['id'],
                ISBN=cls.getISBNIfExists(data['volumeInfo'].get('industryIdentifiers')),
                title=data['volumeInfo'].get('title'),
                subtitle=data['volumeInfo'].get('subtitle'),
                description=data['volumeInfo'].get('description'),
                language=data['volumeInfo'].get('language'),
                pub_date=data['volumeInfo'].get('publishedDate'),
                categories=', '.join(data['volumeInfo'].get('categories'))
                if data['volumeInfo'].get('categories') is not None else None,
                authors=', '.join(data['volumeInfo'].get('authors'))
                if data['volumeInfo'].get('authors') is not None else None
            ) for data in res['items']
        ]

    @staticmethod
    def getISBNIfExists(data: list[dict[str, Any]]) -> str | None:
        if data is None:
            return None
        for i in data:
            if i['type'] == 'ISBN_10':
                return i['identifier']
        return None
