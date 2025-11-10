import os
high = float(c['high'])
low = float(c['low'])
close = float(c['close'])
vol = float(c.get('volume', 0) or 0)
typical = (high + low + close) / 3.0
num += typical * vol
den += vol
last_price = close
vwap = (num / den) if den > 0 else None
return last_price, vwap


# --- logica principal de um poll ---
def poll_once(self):
for a in self.assets:
name = a['name']
try:
if a['source'] == 'coinbase':
candles = self.fetch_coinbase_1min(name, limit=2)
preco, vwap = self.aggregate_to_2min_and_vwap_coinbase(candles)
else:
vals = self.fetch_twelvedata_1min(name, limit=2)
preco, vwap = self.aggregate_to_2min_and_vwap_twelvedata(vals)


sinal = 'NEUTRO'
if preco is not None and vwap is not None:
if float(preco) > float(vwap):
sinal = 'VENDA'
elif float(preco) < float(vwap):
sinal = 'COMPRA'
else:
sinal = 'NEUTRO'


self._signals[name] = {
'preco': float(preco) if preco is not None else None,
'vwap': float(vwap) if vwap is not None else None,
'sinal': sinal,
'updated_at': datetime.now(timezone.utc).isoformat()
}


# Upsert no Supabase (se configurado)
self.upsert_ativo(name, self._signals[name])


except requests.HTTPError as e:
print(f'Falha ao buscar candles {name}:', e)
except Exception as e:
print(f'Erro processando {name}:', e)


def upsert_ativo(self, nome, payload):
if not self.supabase:
return
try:
data = {
'nome': nome,
'preco': payload['preco'],
'vwap': payload['vwap'],
'sinal': payload['sinal'],
'updated_at': payload['updated_at']
}
# usa upsert — precisa que tabela tenha constraint unique em nome
self.supabase.table(self.SUPABASE_TABLE).upsert(data).execute()
except Exception as e:
# Supabase pode devolver error se tabela/constraint não existir
print(f'Erro ao upsertar no Supabase para {nome}:', getattr(e, 'args', e))


# --- getters simples para rota ---
def get_signals(self):
return self._signals


def get_sample_vwap(self):
# usado pela rota /vwap para teste
for s in self._signals.values():
if s['vwap'] is not None:
return s['vwap']
return None
