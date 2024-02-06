from fastapi import status
from starlette.responses import JSONResponse


class ObjectCreated:
    docs = {
        status.HTTP_200_OK: {
            "description": "Returns the ID of the created object as a guarantee of the endpoint triggering",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully created", "id": 0}
                }
            },
        }
    }

    @staticmethod
    def response(id: int):
        return JSONResponse({"message": "Successfully created", "id": id})


class ObjectUpdated:
    docs = {
        status.HTTP_200_OK: {
            "description": "Returns a message indicating a successful update of an object",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully updated"}
                }
            },
        }
    }

    @staticmethod
    def response():
        return JSONResponse({"message": "Successfully updated"})


class ObjectDeleted:
    docs = {
        status.HTTP_200_OK: {
            "description": "Returns a message indicating that the object was successfully deleted",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully deleted"}
                }
            },
        }
    }

    @staticmethod
    def response():
        return JSONResponse({"message": "Successfully deleted"})
