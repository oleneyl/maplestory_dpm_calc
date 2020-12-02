from ..item import ItemKernel as it
from ..item.ItemKernel import ExMDF


def apply_cdr(head: it.Item, base_mdf: ExMDF, cdr: int) -> it.Item:
    if cdr < 0 or cdr > 4:
        raise ValueError("invalid cdr")
    exchange_stat = [0, 9, 12, 21, 30]
    head.set_potential(
        base_mdf + ExMDF(pstat_main=-exchange_stat[cdr], cooltime_reduce=cdr*1000))
    return head
