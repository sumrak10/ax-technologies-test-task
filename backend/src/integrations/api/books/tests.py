import pytest
from src.integrations.api.books.google_books import GoogleBooksAPI, BookAPISchema


@pytest.fixture
def mock_session_client(monkeypatch):
    async def mock_get(url: str, **kwargs):
        if url == '':
            return {
                'id': '123456789',
                'volumeInfo': {
                    'title': 'Test Book',
                    'subtitle': 'Test Subtitle',
                    'description': 'Test Description',
                    'language': 'en',
                    'publishedDate': '2022-01-01',
                    'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': '1234567890'}],
                    'categories': ['Fiction'],
                    'authors': ['Test Author']
                }
            }
        else:
            return {
                'items': [
                    {
                        'id': '123456789',
                        'volumeInfo': {
                            'title': 'Test Book',
                            'subtitle': 'Test Subtitle',
                            'description': 'Test Description',
                            'language': 'en',
                            'publishedDate': '2022-01-01',
                            'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': '1234567890'}],
                            'categories': ['Fiction'],
                            'authors': ['Test Author']
                        }
                    }
                ]
            }

    monkeypatch.setattr(GoogleBooksAPI.session_client, 'get', mock_get)


@pytest.mark.asyncio
async def test_get_by_id():
    book = await GoogleBooksAPI.get_by_id('zyTCAlFPjgYC')
    assert isinstance(book, BookAPISchema)
    assert book.gb_id == 'zyTCAlFPjgYC'
    assert book.ISBN == '0440335701'
    assert book.title == 'The Google Story (2018 Updated Edition)'
    assert book.subtitle == 'Inside the Hottest Business, Media, and Technology Success of Our Time'


# @pytest.mark.asyncio
# async def test_search():
#     books = await GoogleBooksAPI.search(
#         gb_id='123456789',
#         query='Test Query',
#         intitle='Test Title',
#         inauthor='Test Author',
#         isbn='1234567890',
#         categories=['Fiction']
#     )
#     assert isinstance(books, list)
#     assert len(books) == 1
#     book = books[0]
#     assert isinstance(book, BookAPISchema)
#     assert book.gb_id == '123456789'
#     assert book.ISBN == '1234567890'
#     assert book.title == 'Test Book'
#     assert book.subtitle == 'Test Subtitle'
#     assert book.description == 'Test Description'
#     assert book.language == 'en'
#     assert book.pub_date == '2022-01-01'
#     assert book.categories == ['Fiction']
#     assert book.authors == ['Test Author']
