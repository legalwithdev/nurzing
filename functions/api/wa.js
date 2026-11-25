// GET /api/wa -> bounce to WhatsApp without ever printing the number.
// The number lives only in the WHATSAPP_NUMBER environment variable.
import { digits } from './_lib.js';

export async function onRequestGet({ request, env }) {
  const n = digits(env.WHATSAPP_NUMBER || '').replace(/^\+/, '');
  if (!n) return new Response('WhatsApp is not configured', { status: 503 });

  const text = new URL(request.url).searchParams.get('text') || '';
  const target = 'https://wa.me/' + n + (text ? '?text=' + encodeURIComponent(text) : '');

  return new Response(null, {
    status: 302,
    headers: { location: target, 'cache-control': 'no-store' },
  });
}
