from fastapi import APIRouter
from source.transfer.application.use_cases.deposit.controller import deposit
from source.transfer.application.use_cases.history.controller import history

router = APIRouter(prefix="", tags=["transfer"])
# router.add_api_route("/swap", swap, methods=["POST"])
router.add_api_route("/deposit", deposit, methods=["POST"])
router.add_api_route("/user/{user_id}/history", history, methods=["GET"])