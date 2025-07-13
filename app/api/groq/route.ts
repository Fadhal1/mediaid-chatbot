import { NextRequest, NextResponse } from 'next/server';
import Groq from 'groq-sdk';

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

export async function POST(req: NextRequest) {
  const { prompt } = await req.json();
  const completion = await groq.chat.completions.create({
    messages: [
      { role: 'system', content: 'You are MediAid, a Nigerian health-assistant bot. Provide concise, medically-safe advice in ≤ 150 words.' },
      { role: 'user', content: prompt },
    ],
    model: 'llama3-8b-8192',
    temperature: 0.5,
    max_tokens: 180,
  });
  return NextResponse.json({ answer: completion.choices[0]?.message?.content || '' });
}
