from types import SimpleNamespace

from marketplace_service import BuyerUpdate, InfraiChatClient, SellerAsset, stream_and_handoff


class FakeChat:
    def stream(self, *, asset, update):
        yield f"{asset.title}: "
        yield f"received {update.message}"


def test_confirmed_buyer_update_creates_order_handoff():
    asset = SellerAsset("sku-42", "Realtime ledger review", 2500)
    buyer = BuyerUpdate("buyer-7", "Please reserve it")

    reply, order = stream_and_handoff(asset, buyer, FakeChat(), confirmed=True)

    assert reply == "Realtime ledger review: received Please reserve it"
    assert order.accepted is True
    assert order.asset_id == "sku-42"
    assert order.buyer_id == "buyer-7"


def test_stream_skips_chunks_without_choices():
    def chunk(content):
        return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=content))])

    response = [chunk("Hello"), SimpleNamespace(choices=[]), chunk(" there")]
    client = InfraiChatClient.__new__(InfraiChatClient)
    client._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: response))
    )

    assert list(client.stream(
        asset=SellerAsset("sku-42", "Realtime ledger review", 2500),
        update=BuyerUpdate("buyer-7", "Can you deliver this week?"),
    )) == ["Hello", " there"]
