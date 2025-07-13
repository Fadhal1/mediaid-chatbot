// api/chat.js
export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();

  const { message } = req.body;
  if (!message) return res.status(400).json({ error: "No message" });

  try {
    const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama-3.1-8b-instant",
        messages: [{ role: "user", content: message }],
      }),
    });

    const data = await groqRes.json();
    const reply = data.choices?.[0]?.message?.content || "Sorry, I didn’t understand.";
    res.json({ reply });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "AI service error" });
  }
}
