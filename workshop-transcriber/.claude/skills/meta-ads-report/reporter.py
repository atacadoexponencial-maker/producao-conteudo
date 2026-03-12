#!/usr/bin/env python3
"""
Relatório diário Meta Ads + ClickUp → WhatsApp via Evolution API.

Regras de dia:
- Sab/Dom: não gera
- Segunda: cobre Sex+Sab+Dom
- Outros: ontem

SE  = campanhas OUTCOME_LEADS sem 'masterclass' no nome  (funil orderindex=0)
WEB = campanhas OUTCOME_LEADS com 'masterclass' no nome  (funil orderindex=11)
MQL = campo Faturamento Mensal preenchido e != 'Menos de 20 Mil'
"""

import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()

META_TOKEN   = os.environ["META_ACCESS_TOKEN"]
META_ACCOUNT = os.environ["META_AD_ACCOUNT_ID"]
CU_KEY       = os.environ["CLICKUP_API_KEY"]
EVO_URL      = os.environ["EVOLUTION_API_URL"].rstrip("/")
EVO_INSTANCE = os.environ["EVOLUTION_INSTANCE"]
EVO_KEY      = os.environ["EVOLUTION_API_KEY"]
EVO_NUMBER   = os.environ["EVOLUTION_WHATSAPP_NUMBER"]

CRM_LIST_ID  = "205126080"
FUNIL_CF_ID  = "a663b002-661c-4dc1-86c3-612e94f3a447"  # dropdown 🔻 Funil
SE_IDX       = 0   # SESSÃO ESTRATÉGICA
WEB_IDX      = 11  # WEBINAR

GRAPH = "https://graph.facebook.com/v21.0"
CU    = "https://api.clickup.com/api/v2"
TZ    = timezone(timedelta(hours=-3))  # BRT


# ── Período ───────────────────────────────────────────────────────────────────

def get_period():
    today = date.today()
    wd = today.weekday()  # 0=Seg … 6=Dom
    if wd in (5, 6):
        return None, None, None
    if wd == 0:
        start = today - timedelta(days=3)
        end   = today - timedelta(days=1)
        label = f"{start.strftime('%d/%m')} a {end.strftime('%d/%m')}"
    else:
        start = end = today - timedelta(days=1)
        label = start.strftime("%d/%m")
    return start, end, label


def day_ms(d: date, end=False) -> int:
    t = datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=TZ) if end \
        else datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=TZ)
    return int(t.timestamp() * 1000)


# ── Meta Ads ──────────────────────────────────────────────────────────────────

def meta_spend(start: date, end: date):
    tr = json.dumps({"since": str(start), "until": str(end)})

    # Campanhas ativas OUTCOME_LEADS
    r = httpx.get(f"{GRAPH}/{META_ACCOUNT}/campaigns", params={
        "fields": "id,name,objective",
        "filtering": json.dumps([{"field": "effective_status", "operator": "IN", "value": ["ACTIVE"]}]),
        "access_token": META_TOKEN,
    })
    r.raise_for_status()
    leads = [c for c in r.json().get("data", []) if c["objective"] == "OUTCOME_LEADS"]
    se_ids  = [c["id"] for c in leads if "masterclass" not in c["name"].lower()]
    web_ids = [c["id"] for c in leads if "masterclass"     in c["name"].lower()]

    total = _account_spend(tr)
    se    = _campaigns_spend(se_ids,  tr)
    web   = _campaigns_spend(web_ids, tr)
    return total, se, web


def _account_spend(tr: str) -> float:
    r = httpx.get(f"{GRAPH}/{META_ACCOUNT}/insights",
                  params={"fields": "spend", "time_range": tr, "access_token": META_TOKEN})
    r.raise_for_status()
    data = r.json().get("data", [])
    return float(data[0]["spend"]) if data else 0.0


def _campaigns_spend(ids: list, tr: str) -> float:
    total = 0.0
    for cid in ids:
        r = httpx.get(f"{GRAPH}/{cid}/insights",
                      params={"fields": "spend", "time_range": tr, "access_token": META_TOKEN})
        r.raise_for_status()
        data = r.json().get("data", [])
        if data:
            total += float(data[0]["spend"])
    return total


# ── ClickUp ───────────────────────────────────────────────────────────────────

def clickup_leads(start: date, end: date):
    start_ms = day_ms(start) - 1
    end_ms   = day_ms(end, end=True) + 1
    headers  = {"Authorization": CU_KEY}

    tasks, page = [], 0
    while True:
        r = httpx.get(f"{CU}/list/{CRM_LIST_ID}/task", headers=headers, params={
            "date_created_gt": start_ms,
            "date_created_lt": end_ms,
            "include_closed": "true",
            "subtasks": "false",
            "page": page,
        })
        r.raise_for_status()
        batch = r.json().get("tasks", [])
        tasks.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    se_leads = se_mqls = web_leads = web_mqls = 0
    for t in tasks:
        funil_val = None
        fat_val   = ""
        for cf in t.get("custom_fields", []):
            if cf.get("id") == FUNIL_CF_ID:
                funil_val = cf.get("value")
            if "Faturamento Mensal" in (cf.get("name") or ""):
                fat_val = cf.get("value") or ""

        is_mql = bool(fat_val) and fat_val != "Menos de 20 Mil"

        if funil_val == SE_IDX:
            se_leads += 1
            if is_mql: se_mqls += 1
        elif funil_val == WEB_IDX:
            web_leads += 1
            if is_mql: web_mqls += 1

    return se_leads, se_mqls, web_leads, web_mqls


# ── Formatação ────────────────────────────────────────────────────────────────

def brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def build_report(label, total, se_spend, se_leads, se_mqls, web_spend, web_leads, web_mqls) -> str:
    se_cpl    = se_spend  / se_leads  if se_leads  else 0
    se_cp_mql = se_spend  / se_mqls   if se_mqls   else 0
    web_cpl   = web_spend / web_leads if web_leads else 0

    lines = [
        f"🗓️ Dia: {label}",
        "",
        f"Investido geral: {brl(total)}",
        "",
        "SE",
        f"Investido: {brl(se_spend)}",
        f"Novos leads: {se_leads}",
        f"MQLs: {se_mqls}",
        f"CPL: {brl(se_cpl)}",
    ]
    if se_mqls:
        lines.append(f"CP-MQL: {brl(se_cp_mql)}")
    lines += [
        "",
        "WEB",
        f"Investido: {brl(web_spend)}",
        f"Novos leads: {web_leads}",
        f"MQLs: {web_mqls}",
        f"CPL: {brl(web_cpl)}",
    ]
    if web_mqls:
        web_cp_mql = web_spend / web_mqls
        lines.append(f"CP-MQL: {brl(web_cp_mql)}")
    return "\n".join(lines)


# ── WhatsApp ──────────────────────────────────────────────────────────────────

def send_whatsapp(text: str):
    r = httpx.post(
        f"{EVO_URL}/message/sendText/{EVO_INSTANCE}",
        headers={"apikey": EVO_KEY, "Content-Type": "application/json"},
        json={"number": EVO_NUMBER, "text": text},
    )
    r.raise_for_status()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    start, end, label = get_period()
    if not start:
        sys.exit(0)  # fim de semana, silencioso

    total, se_spend, web_spend           = meta_spend(start, end)
    se_leads, se_mqls, web_leads, web_mqls = clickup_leads(start, end)

    report = build_report(label, total, se_spend, se_leads, se_mqls, web_spend, web_leads, web_mqls)
    send_whatsapp(report)
    print(report)


if __name__ == "__main__":
    main()
