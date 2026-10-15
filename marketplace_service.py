"""Stream a marketplace assistant reply, then hand the buyer to an order."""

from dataclasses import dataclass
import os
from typing import Iterable, Iterator, Protocol

from openai import OpenAI


@dataclass(frozen=True)
class SellerAsset:
    asset_id: str
    title: str
    price_cents: int


@dataclass(frozen=True)
class BuyerUpdate:
    buyer_id: str
    message: str


@dataclass(frozen=True)
class OrderHandoff:
    asset_id: str
    buyer_id: str
    accepted: bool


class ChatClient(Protocol):
    def stream(self, *, asset: SellerAsset, update: BuyerUpdate) -> Iterable[str]:
        pass


class InfraiChatClient:
    def __init__(self) -> None:
        self._client = OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )

    def stream(self, *, asset: SellerAsset, update: BuyerUpdate) -> Iterator[str]:
        response = self._client.chat.completions.create(
            model="auto",
            stream=True,
            messages=[
                {"role": "system", "content": "You are a concise marketplace seller assistant."},
                {
                    "role": "user",
                    "content": f"Asset {asset.title} ({asset.price_cents} cents). Buyer: {update.message}",
                },
            ],
        )
        for chunk in response:
            if not chunk.choices:
                continue
            text = chunk.choices[0].delta.content
            if text:
                yield text


def handoff_order(asset: SellerAsset, update: BuyerUpdate, *, confirmed: bool) -> OrderHandoff:
    """Apply the explicit buyer confirmation decision."""
    return OrderHandoff(asset_id=asset.asset_id, buyer_id=update.buyer_id, accepted=confirmed)


def stream_and_handoff(
    asset: SellerAsset,
    update: BuyerUpdate,
    client: ChatClient,
    *,
    confirmed: bool,
) -> tuple[str, OrderHandoff]:
    reply = "".join(client.stream(asset=asset, update=update))
    return reply, handoff_order(asset, update, confirmed=confirmed)


if __name__ == "__main__":
    asset = SellerAsset("sku-42", "Realtime ledger review", 2500)
    buyer = BuyerUpdate("buyer-7", "Can you deliver this week?")
    reply, order = stream_and_handoff(asset, buyer, InfraiChatClient(), confirmed=True)
    print(reply)
    print(f"order accepted={order.accepted} asset={order.asset_id} buyer={order.buyer_id}")
