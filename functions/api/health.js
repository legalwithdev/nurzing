import { json } from './_lib.js';

export async function onRequestGet({ env }) {
  let db = 'not bound';
  if (env.DB) {
    try {
      await env.DB.prepare('SELECT 1').all();
      db = 'ok';
    } catch (err) {
      db = 'error';
    }
  }
  return json({
    ok: true,
    service: 'nurzing',
    db,
    whatsapp: env.WHATSAPP_NUMBER ? 'set' : 'missing',
    admin_key: env.ADMIN_KEY ? 'set' : 'missing',
    time: new Date().toISOString(),
  });
}
