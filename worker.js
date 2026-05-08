const MODELS = [
  'llama-3.3-70b-versatile', // 14,400 RPD，主力
  'llama-3.1-8b-instant',    // 快速備援
];

export default {
  async fetch(request, env) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') return new Response(null, { headers: corsHeaders });
    if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });

    let prompt;
    try { ({ prompt } = await request.json()); }
    catch { return new Response('Bad Request', { status: 400 }); }
    if (!prompt || prompt.length > 4000) return new Response('Bad Request', { status: 400 });

    for (const model of MODELS) {
      const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${env.GROQ_KEY}`,
        },
        body: JSON.stringify({
          model,
          messages: [
            {
              role: 'system',
              content: '你是量化交易投資人。直接輸出最終文章正文，嚴禁輸出規劃步驟、草稿標記、輸入資料整理、需求說明、自我評估、核查清單或任何形式的免責聲明。',
            },
            { role: 'user', content: prompt },
          ],
          max_tokens: 2000,
          temperature: 0.7,
        }),
      });

      const data = await res.json();

      if (res.status === 429 || res.status >= 500) continue;

      if (!res.ok) {
        return new Response(JSON.stringify({ error: data }), {
          status: 502,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      const text = data?.choices?.[0]?.message?.content ?? '';
      const finishReason = data?.choices?.[0]?.finish_reason ?? 'unknown';
      return new Response(JSON.stringify({ text, finishReason, model }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({ error: 'All models quota exceeded. Please retry tomorrow.' }), {
      status: 429,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  },
};
