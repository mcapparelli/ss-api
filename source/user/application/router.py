from fastapi import APIRouter
from source.user.application.use_cases.create_user.controller import create_user

router = APIRouter(prefix="/users", tags=["users"])
router.add_api_route("", create_user, methods=["POST"])