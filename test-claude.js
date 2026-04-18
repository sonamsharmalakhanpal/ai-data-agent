import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function run() {
  const msg = await client.messages.create({
    model: "claude-3-5-haiku-20241022",
    max_tokens: 200,
    messages: [
      { role: "user", content: "Explain REST API in simple terms" }
    ],
  });

  console.log(msg.content[0].text);
}

run().catch((error) => {
  console.error("Error:", error.message);
  process.exit(1);
});