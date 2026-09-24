# P1 Evidence Explorer - checkpoint 01

Ngay: 17/09/2026  
Product repo: `D:/ANNAM/TradingWorkspace/projects/mt5-tradingview-backtester`  
Trang thai: **backend read-only slice da trien khai; P1 chua hoan thanh**.

## Hanh vi da thay doi

Da them mot application shell Flask rieng cho P1, khong import `app.py` hoac `mt5_data.py`. Shell nay chi doc session artifact da luu va cung cap read model theo luong:

`run -> provenance/assumptions -> ledger -> metrics-v1 -> equity/trade inspector`

Endpoint hien co:

- `GET /api/runs`
- `GET /api/runs/<id>`
- `GET /api/runs/<id>/ledger`
- `GET /api/runs/<id>/metrics`
- `GET /api/runs/<id>/equity`
- `GET /api/runs/<id>/trades/<trade_id>`

P1 shell khong co execution endpoint. SQLite duoc mo `mode=ro`; missing database tra `READ_FAILURE` va khong tao file moi.

## Data/state flow

`p1_app.py` chi lam HTTP shell. `evidence_store.py` la read-only adapter tu schema replay session legacy sang P1 read model. `evidence_metrics.py` la business core thuần cho `metrics-v1`.

Artifact legacy khong co dataset version, requested/observed range, cost model, risk model, engine/config hash hoac planned risk budget. P1 khong suy dien cac field nay: tra `null`/`unknown` va `comparison.ready=false`. Field `r` legacy chi duoc giu de doi chieu; official realized R khong lay tu field nay.

## Quyet dinh va trade-off

- Giu Flask cho shell P1 dau tien de giam blast radius; chua can FastAPI migration.
- Khong sua `SessionStore` cu vi no tu khoi tao SQLite va co write path. P1 dung reader rieng de bao dam read path khong migrate/ghi.
- Legacy `profit` duoc map vao net P/L vi schema cu dung no de tinh `stats.net`; gross P/L va fees van de `null` vi artifact khong du provenance de tach lai.
- Profit factor duoc tinh sau cost tu net P/L; BE ngat loss streak theo contract.

## Kiem chung

Focused suite:

```text
Ran 8 tests in 0.558s
OK
```

Regression suite toan bo repo:

```text
Ran 10 tests in 0.611s
OK
```

Baseline `metrics-v1` synthetic 5 trades khop contract P0: 2 win / 2 loss / 1 BE, gross P/L 30, fees 8, net 22, win rate 40%, profit factor 1.5, expectancy 4.4, average R 0.15R, max DD 32, max DD% `32/1048`, max loss streak 1, ending balance 1022.

Test cung khoa cac invariant: import P1 khong import `app`/`mt5_data`; execution route khong ton tai; read path khong doi mtime DB; missing DB khong duoc tu tao; hai run fixture doc duoc qua cung read model.

Regression suite cu van in `[SocketServer] Listening on 127.0.0.1:9000...` khi `test_session_api.py` import `app.py`. Day la blocker lifecycle da ghi o P0, khong phai side effect cua P1 shell.

## Con lai truoc khi dat P1

- Chua verify hai artifact that trong `data/sessions.sqlite3`; lan thu doc truc tiep DB bi runtime policy chan, nen checkpoint nay chi dung fixture synthetic.
- Chua co UI Evidence Explorer/export.
- Chua co replay/chart cutoff fixture tren P1 adapter.
- Chua co artifact schema moi mang day du provenance/cost/risk/version; legacy session chi duoc doc voi unknown fields ro rang.
