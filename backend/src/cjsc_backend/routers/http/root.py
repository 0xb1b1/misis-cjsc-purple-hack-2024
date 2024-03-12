from fastapi import APIRouter

router = APIRouter(
    tags=["API Information"],
)


@router.get("/")
async def root_welcome() -> dict:
    """Welcome the user to the API and provide a link to the documentation.

    Returns:
        dict: A welcome message wrapped in JSON.
    """
    return {
        "message": "Welcome to the CJSC Backend API.\n\n\
Please visit the API documentation at `/docs`."
    }
