from source.transfer.domain.entities.transfer_entity import Transfer

class SwapResult:
    def __init__(self, credit: Transfer, debit: Transfer):
        self.credit = credit
        self.debit = debit 