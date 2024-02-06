import uvicorn

from config.server import server_settings


if __name__ == '__main__':
    uvicorn.run("src.main:app", host='0.0.0.0', port=server_settings.PORT)
