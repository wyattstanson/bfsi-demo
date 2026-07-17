from __future__ import annotations

import io
import sys
import time

from app.layer1_data import db, seed


def _copy_pg(rows, table, cols):
    conn = db.conn()
    buf = io.StringIO()
    for r in rows:
        buf.write("\t".join("" if v is None else str(v).replace("\t", " ").replace("\n", " ")
                            for v in r) + "\n")
    buf.seek(0)
    with conn.cursor() as cur:
        with cur.copy(f"COPY {table} ({','.join(cols)}) FROM STDIN") as cp:
            cp.write(buf.read())


def bulk(n: int, batch: int = 50000) -> dict:
    db.init_schema()
    db.execute("DELETE FROM txn")
    db.execute("DELETE FROM party")
    pg = db.backends()["ledger"] == "postgres"
    pcols = ["party_id", "domain", "journey_stage", "region", "currency", "name",
             "email", "ssn", "age", "income", "balance", "tenure_months", "risk_band",
             "fairness_group", "consent_ref", "consent_marketing"]
    total_p = total_t = 0
    for start in range(0, n, batch):
        end = min(start + batch, n)
        parties = [seed._make_party(i) for i in range(start, end)]
        txns = []
        for p in parties:
            txns.extend(seed._make_txns(p[0], 12))
        if pg:
            _copy_pg(parties, "party", pcols)
            _copy_pg(txns, "txn", ["party_id", "ts", "amount", "mcc", "channel", "is_flagged"])
        else:
            db.executemany(
                "INSERT INTO party (" + ",".join(pcols) + ") VALUES (" + ",".join(["?"] * 16) + ")",
                parties)
            db.executemany(
                "INSERT INTO txn (party_id, ts, amount, mcc, channel, is_flagged) VALUES (?,?,?,?,?,?)",
                txns)
        total_p += len(parties)
        total_t += len(txns)
        print(f"  {total_p:,} parties, {total_t:,} txns")
    return {"parties": total_p, "txns": total_t, "backend": db.backends()["ledger"]}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    t0 = time.time()
    print(bulk(n), f"in {time.time() - t0:.1f}s")
