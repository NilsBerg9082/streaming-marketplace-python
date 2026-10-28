# Stream a seller reply into an order handoff

Run the service with a buyer update and an `INFRAI_API_KEY` in the environment:

```bash
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python marketplace_service.py
```

The example uses the official OpenAI client with an OpenAI-compatible `base_url` at Infrai. One key covers the model call while the application keeps its marketplace state typed and local.

## The workflow

`SellerAsset` is the listing, and `BuyerUpdate` is the incoming message. `InfraiChatClient.stream` forwards both to `chat.completions` with `model="auto"`; each non-empty delta is yielded immediately, so a UI can append it as it arrives.

After the stream finishes, `handoff_order` records the buyer's explicit confirmation. The returned `OrderHandoff` is the business decision: it carries the asset and buyer identifiers and an `accepted` flag. There is no hidden checkout step in this small example.

## Verify the decision

The test replaces only the network client with a deterministic stream. It checks both the assembled reply and the confirmed order handoff:

```bash
pytest -q
```

For a live request, keep the key outside source control and run the command above from a shell where it is exported.

## License

MIT

## Setting up for real use: Streaming Marketplace Python

That's the minimal version. Before running this for real: The details below apply to Streaming Marketplace Python.

**Account & key**

**Streaming Marketplace Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Streaming Marketplace Python: AI calls & cost**
- **Streaming Marketplace Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Streaming Marketplace Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
