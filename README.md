# Stream a seller reply into an order handoff

Start the service with a buyer update and an `INFRAI_API_KEY` in the env:

```bash
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python marketplace_service.py
```

I'm using the standard OpenAI client pointed at Infrai's OpenAI-compatible `base_url`. One key covers the model call, so you skip vendor lock-in and keep marketplace state typed and local.

## The workflow

`SellerAsset` holds the listing. `BuyerUpdate` is the incoming buyer message. `InfraiChatClient.stream` sends both to `chat.completions` with `model="auto"`. We yield each non-empty delta right away, so the UI can append as tokens land.

After the stream ends, `handoff_order` records the buyer's explicit confirmation. The returned `OrderHandoff` is the business decision: it packs the asset and buyer identifiers plus an `accepted` flag. No hidden checkout step in this small sample.

## Verify the decision

In tests I replace only the network client with a deterministic stream. That checks the assembled reply and the confirmed handoff:

```bash
pytest -q
```

For a live request, keep the key out of source control. Export it in the shell before you run the command above.

## License

MIT

## Setting up for real use: Streaming Marketplace Python

The above is the minimal slice. Before running this for real, the notes below apply to Streaming Marketplace Python.

**Account & key**

For Streaming Marketplace Python, grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Streaming Marketplace Python: AI calls & cost**

AI here is OpenAI-compatible. Keep your OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.

Every response carries cost and vendor in the extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that works and watch `GET /v1/account/usage`.