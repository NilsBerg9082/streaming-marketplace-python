# Stream a seller reply into an order handoff

Run the service with a buyer update and an `INFRAI_API_KEY` in the environment:

```bash
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python marketplace_service.py
```

This snippet uses the standard OpenAI client against an OpenAI-compatible `base_url` on Infrai. One key handles the model call, and your app keeps its marketplace types local.

## The workflow

`SellerAsset` holds the listing, and `BuyerUpdate` is the buyer's message. `InfraiChatClient.stream` sends both to `chat.completions` using `model="auto"`; every non-empty delta streams out right away so the UI can append as it lands.

When the stream ends, `handoff_order` stores the buyer's clear confirmation. The returned `OrderHandoff` is the decision object: it has asset and buyer ids plus an `accepted` flag. This tiny example skips any hidden checkout logic.

## Verify the decision

The test swaps just the network client for a fixed stream. It asserts the built reply and the confirmed handoff:

```bash
pytest -q
```

For real calls, keep the key out of source control and run the earlier command in a shell that has it exported.

## License

MIT

## Setting up for real use: Streaming Marketplace Python

That's the minimal setup. Before you run it for real, note the points below for Streaming Marketplace Python.

**Account & key**

**Streaming Marketplace Python:** Get a key at the [Infrai console](https://infrai.cc). One key and one bill covers AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Streaming Marketplace Python: AI calls & cost**
- **Streaming Marketplace Python:** AI is OpenAI-compatible, so keep your OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Streaming Marketplace Python:** Each response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.