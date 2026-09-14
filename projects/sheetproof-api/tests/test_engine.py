import io
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import analyze, read_upload  # noqa: E402
from app.main import read_workbook  # noqa: E402


def issues_by_check(result, name):
    return [x for x in result.get("all_issues", []) if x["check"] == name]


def analyze_full(df):
    # analyze() intentionally returns only preview to the UI; monkey-style recreate by using preview where sufficient
    result = analyze(df)
    return result


def test_clean_table_has_no_issues():
    df = pd.DataFrame({
        "SKU": ["A001", "A002", "A003", "A004", "A005"],
        "수량": [1, 2, 3, 4, 5],
        "단가": [1000, 2000, 3000, 4000, 5000],
        "금액": [1000, 4000, 9000, 16000, 25000],
        "날짜": ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05"],
    })
    r = analyze(df)
    assert r["issues_total"] == 0, r


def test_detects_duplicate_and_arithmetic_error():
    df = pd.DataFrame({
        "SKU": ["A001", "A002", "A002", "A004"],
        "수량": [1, 2, 3, 4],
        "단가": [1000, 2000, 3000, 4000],
        "금액": [1000, 4000, 9500, 16000],
    })
    r = analyze(df)
    checks = [x["check"] for x in r["preview"]]
    assert r["issues_total"] >= 2
    assert "중복 키" in checks or r["high"] >= 2


def test_date_formats_mixed_are_flagged():
    df = pd.DataFrame({
        "날짜": ["2026-09-01", "2026-09-02", "2026/09/03", "2026-09-04"],
        "값": [1, 2, 3, 4],
    })
    r = analyze(df)
    assert r["low"] >= 1, r


def test_non_date_column_with_korean_il_character_is_not_date_candidate():
    # '판매일수' contains '일' but is a duration/count, not a date column.
    df = pd.DataFrame({
        "판매일수": [1, 2, 3, 4, 5],
        "SKU": ["A", "B", "C", "D", "E"],
    })
    r = analyze(df)
    assert r["issues_total"] == 0, r


def test_numeric_text_currency_is_accepted():
    df = pd.DataFrame({
        "SKU": ["A", "B", "C", "D"],
        "단가": ["₩1,000", "2,000", "$3,000", "4000"],
        "수량": [1, 1, 1, 1],
        "금액": [1000, 2000, 3000, 4000],
    })
    r = analyze(df)
    assert r["issues_total"] == 0, r


def test_missing_value_in_mostly_populated_column_is_flagged():
    df = pd.DataFrame({
        "SKU": ["A", "B", "C", "D", None, "F", "G", "H", "I", "J"],
        "수량": list(range(1, 11)),
    })
    r = analyze(df)
    assert r["high"] >= 1, r


def test_cp949_csv_read(tmp_path):
    df = pd.DataFrame({"상품코드": ["A1", "A2"], "수량": [1, 2]})
    raw = df.to_csv(index=False).encode("cp949")
    out = read_upload("sample.csv", raw)
    assert list(out.columns) == ["상품코드", "수량"]
    assert len(out) == 2


def test_api_upload_sample_xlsx():
    from fastapi.testclient import TestClient
    from app import app
    client = TestClient(app)
    sample = ROOT / "tests" / "fixtures" / "sample_test.xlsx"
    with sample.open("rb") as f:
        resp = client.post(
            "/api/analyze",
            files={"file": (sample.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "sample_test.xlsx"
    assert data["issues_total"] == 4
    assert data["high"] == 2
    assert data["medium"] == 1
    assert data["low"] == 1


def test_realistic_clean_fixture_has_no_issues():
    sample = ROOT / "tests" / "fixtures" / "ecommerce_clean.xlsx"
    df = read_upload(sample.name, sample.read_bytes())
    r = analyze(df)
    assert r["issues_total"] == 0, r


def test_realistic_broken_fixture_detects_multiple_classes():
    sample = ROOT / "tests" / "fixtures" / "ecommerce_broken.xlsx"
    df = read_upload(sample.name, sample.read_bytes())
    r = analyze(df)
    checks = {x["check"] for x in r["preview"]}
    assert r["issues_total"] >= 4, r
    assert r["high"] >= 2, r
    assert "중복 키" in checks or r["high"] >= 2
    assert "산술 불일치" in checks or r["high"] >= 2


def test_realistic_cp949_invoice_fixture():
    sample = ROOT / "tests" / "fixtures" / "invoice_broken_cp949.csv"
    df = read_upload(sample.name, sample.read_bytes())
    r = analyze(df)
    assert r["issues_total"] >= 2, r
    assert r["high"] >= 2, r


def test_multisheet_workbook_reports_sheet_locations():
    from io import BytesIO
    from fastapi.testclient import TestClient
    from app import app

    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        pd.DataFrame({
            "SKU": ["A", "A", "C", "D"],
            "수량": [1, 2, 3, 4],
            "단가": [10, 10, 10, 10],
            "금액": [10, 20, 30, 40],
        }).to_excel(writer, index=False, sheet_name="주문")
        pd.DataFrame({
            "SKU": ["X", "Y", "Z", "W"],
            "수량": [1, 1, 1, 1],
            "단가": [5, 5, 5, 5],
            "금액": [5, 5, 5, 6],
        }).to_excel(writer, index=False, sheet_name="정산")

    client = TestClient(app)
    resp = client.post(
        "/api/analyze",
        files={"file": ("multi.xlsx", bio.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["sheets"] == 2
    assert data["issues_total"] >= 2
    assert {item["sheet"] for item in data["preview"]} <= {"주문", "정산"}
    assert any(item["sheet"] == "정산" and item["check"] == "산술 불일치" for item in data["preview"])


def test_csv_report_download_contains_structured_locations():
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    sample = ROOT / "tests" / "fixtures" / "ecommerce_broken.xlsx"
    with sample.open("rb") as f:
        resp = client.post(
            "/api/report/csv",
            files={"file": (sample.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert resp.status_code == 200
    text = resp.content.decode("utf-8-sig")
    assert "severity,check,sheet,row,column,value,message,suggestion" in text
    assert "Sheet1" in text


def test_json_report_download_has_all_issues():
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    sample = ROOT / "tests" / "fixtures" / "ecommerce_broken.xlsx"
    with sample.open("rb") as f:
        resp = client.post(
            "/api/report/json",
            files={"file": (sample.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["all_issues"]) == data["issues_total"]
    assert all("sheet" in issue and "row" in issue and "column" in issue for issue in data["all_issues"])


def test_health_version_matches_app_version():
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["version"] == "0.3.0-pre"


# ---------------------------------------------------------------------------
# Regression tests for the v0.3-pre code review fixes (Fix Now items 1-5)
# ---------------------------------------------------------------------------

def test_korean_compound_column_names_are_recognized():
    """'판매단가'/'출고수량'/'합계금액'/'품목코드' are realistic Korean column
    names that must be recognized as price/qty/amount/id columns even though
    they are compound words with no separator before the 2-char hint."""
    df = pd.DataFrame({
        "품목코드": ["A", "A", "B", "C"],
        "출고수량": [1, 2, 3, 4],
        "판매단가": [1000, 2000, 3000, 4000],
        "합계금액": [1000, 4000, 9500, 16000],  # 3*3000=9000 != 9500
    })
    r = analyze(df)
    checks = {x["check"] for x in r["preview"]}
    assert r["issues_total"] >= 2, r
    assert "중복 키" in checks, r
    assert "산술 불일치" in checks, r


def test_english_words_containing_hint_substrings_are_not_falsely_flagged():
    """'postcode'/'keyword' legitimately contain 'code'/'key' as a substring
    but are not ID/SKU-style unique columns; repeated values in them must
    not be reported as duplicate-key violations."""
    df = pd.DataFrame({
        "postcode": ["06134", "06134", "03187", "03187", "04524"],
        "keyword": ["sale", "sale", "new", "new", "hot"],
        "customer": ["A", "B", "C", "D", "E"],
    })
    r = analyze(df)
    assert r["issues_total"] == 0, r


def test_phone_and_postal_code_columns_are_not_treated_as_id_columns():
    """'전화번호'/'우편번호' contain the '번호' hint substring but are normal,
    legitimately-repeating attributes, not identifier columns. Regression
    test: broadening '번호' to match Korean compound words also made these
    match, so duplicate phone/postal-code values were wrongly reported as
    '중복 키' (duplicate key) violations."""
    df = pd.DataFrame({
        "전화번호": ["010-1111-2222", "010-1111-2222", "010-3333-4444"],
        "우편번호": ["06134", "03187", "06134"],
        "고객명": ["A", "B", "C"],
    })
    r = analyze(df)
    assert r["issues_total"] == 0, r


def test_order_and_business_number_columns_still_detected_as_id_columns():
    """'주문번호'/'사업자번호' ARE genuine identifiers (unlike '전화번호'/
    '우편번호' above) and duplicate values in them must still be flagged."""
    df = pd.DataFrame({
        "주문번호": ["ORD1", "ORD1", "ORD2", "ORD3"],
        "품목": ["A", "B", "C", "D"],
    })
    r = analyze(df)
    assert any(x["check"] == "중복 키" for x in r["preview"]), r

    df2 = pd.DataFrame({
        "사업자번호": ["111-22-33333", "111-22-33333", "222-33-44444"],
        "상호": ["A", "B", "C"],
    })
    r2 = analyze(df2)
    assert any(x["check"] == "중복 키" for x in r2["preview"]), r2


def test_title_row_above_real_header_is_detected_with_correct_row_numbers():
    """Common Korean template layout: row 1 is a report title in a merged
    cell, row 2 is the real header, data starts on row 3. The engine must
    find the real header row and report spreadsheet-accurate row numbers,
    not treat the title row as headers and the real header row as data."""
    from io import BytesIO

    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        raw_rows = pd.DataFrame([
            ["9월 판매 실적", None, None, None],
            ["SKU", "수량", "단가", "금액"],
            ["A001", 1, 1000, 1000],
            ["A002", 2, 2000, 3000],  # excel row 4: expected 4000, got 3000
            ["A003", 3, 3000, 9000],
        ])
        raw_rows.to_excel(writer, index=False, header=False, sheet_name="실적")

    sheets = read_workbook("title_row.xlsx", bio.getvalue())
    df = sheets["실적"]
    assert list(df.columns) == ["SKU", "수량", "단가", "금액"], df.columns.tolist()

    r = analyze(df, sheet="실적", include_all=True)
    arithmetic_issues = [x for x in r["all_issues"] if x["check"] == "산술 불일치"]
    assert arithmetic_issues, r["all_issues"]
    assert arithmetic_issues[0]["row"] == 4, arithmetic_issues[0]


def test_sparse_real_header_is_not_mistaken_for_a_title_row():
    """A real (if sparsely-labeled) header row -- only the first column
    named, the rest blank, as when someone only bothered to label the key
    column -- must NOT be discarded in favor of promoting the first data
    row to be the header. Regression test: this exact shape (one named
    header cell, rest 'Unnamed:') previously matched the same 'Unnamed:'
    ratio as a genuine title row and got incorrectly swapped, silently
    losing the header and the first data row."""
    from io import BytesIO

    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        raw_rows = pd.DataFrame([
            ["고객명", None, None, None],
            ["홍길동", "서울", "010-1", "VIP"],
            ["김철수", "부산", "010-2", "일반"],
        ])
        raw_rows.to_excel(writer, index=False, header=False, sheet_name="고객")

    sheets = read_workbook("sparse_header.xlsx", bio.getvalue())
    df = sheets["고객"]
    assert df.columns.tolist()[0] == "고객명", df.columns.tolist()
    assert len(df) == 2, "both real data rows must be preserved, none promoted to header"
    assert "홍길동" in df.iloc[:, 0].tolist()


def test_csv_report_neutralizes_formula_injection_values():
    """A cell value starting with '=', '+', '-', or '@' from an untrusted
    uploaded file must not be written raw into the downloadable CSV report,
    since spreadsheet software treats such leading characters as a formula
    trigger when the report is opened (CSV/Formula Injection, CWE-1236).

    The payload is delivered via a CSV upload (not xlsx): writing a python
    string starting with '=' into an xlsx cell via openpyxl stores it as a
    live formula rather than literal text, which would not exercise the
    literal-string code path this fix targets. CSV has no formula concept,
    so the value always survives as literal text, exactly like a real
    attacker-controlled text cell would.
    """
    from fastapi.testclient import TestClient
    from app import app

    csv_bytes = (
        "SKU,수량,단가,금액\n"
        "A001,1,=1+1,1000\n"
        "A001,2,2000,4000\n"
        "A003,3,3000,9000\n"
        "A004,4,4000,16000\n"
    ).encode("utf-8-sig")

    client = TestClient(app)
    resp = client.post(
        "/api/report/csv",
        files={"file": ("injection.csv", csv_bytes, "text/csv")},
    )
    assert resp.status_code == 200
    text = resp.content.decode("utf-8-sig")
    assert ",=1+1," not in text, text  # raw/unescaped formula must not appear
    assert "'=1+1" in text, text  # neutralized (quote-prefixed) form must appear


def test_large_upload_does_not_block_a_concurrent_small_request(monkeypatch):
    """A slow analysis (large/legal-size file) must not block other
    concurrent requests, since app.main runs a single asyncio event loop.
    The heavy work is simulated with a short sleep instead of a real large
    file so the test stays fast and deterministic."""
    import asyncio
    import time as time_module

    import httpx
    from app import main as main_module

    original_load_and_analyze = main_module.load_and_analyze

    def maybe_slow_load_and_analyze(file, raw, *, include_all=False):
        if file.filename == "slow.xlsx":
            time_module.sleep(0.6)
        return original_load_and_analyze(file, raw, include_all=include_all)

    monkeypatch.setattr(main_module, "load_and_analyze", maybe_slow_load_and_analyze)

    sample = ROOT / "tests" / "fixtures" / "sample_test.xlsx"
    sample_bytes = sample.read_bytes()

    async def run():
        transport = httpx.ASGITransport(app=main_module.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            async def call(filename, delay=0.0):
                if delay:
                    await asyncio.sleep(delay)
                t0 = time_module.time()
                resp = await client.post(
                    "/api/analyze",
                    files={"file": (filename, sample_bytes,
                                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                )
                return resp.status_code, time_module.time() - t0

            slow_call = call("slow.xlsx")
            fast_call = call("fast.xlsx", delay=0.1)
            (slow_status, slow_dur), (fast_status, fast_dur) = await asyncio.gather(slow_call, fast_call)
            return slow_status, slow_dur, fast_status, fast_dur

    slow_status, slow_dur, fast_status, fast_dur = asyncio.run(run())
    assert slow_status == 200
    assert fast_status == 200
    # The fast request started 0.1s after the slow one and must finish long
    # before the slow one's ~0.6s artificial delay is over if the event loop
    # was not blocked.
    assert fast_dur < 0.4, f"fast request took {fast_dur:.2f}s (event loop likely blocked)"


def test_allowed_origins_env_var_is_parsed_cleanly():
    """ALLOWED_ORIGINS is a comma-separated env var; blank/whitespace-only
    entries (including an unset/empty value) must not become a stray '' or
    ' ' origin in the allow-list."""
    from app.main import parse_allowed_origins

    assert parse_allowed_origins(None) == []
    assert parse_allowed_origins("") == []
    assert parse_allowed_origins("   ") == []
    assert parse_allowed_origins("https://cosuma.co.kr") == ["https://cosuma.co.kr"]
    assert parse_allowed_origins(
        "https://cosuma.co.kr, https://preview.vercel.app ,,"
    ) == ["https://cosuma.co.kr", "https://preview.vercel.app"]


def test_cors_is_disabled_by_default_and_enabled_via_allowed_origins(monkeypatch):
    """No ALLOWED_ORIGINS configured -> no CORS middleware at all, so a
    cross-origin browser request gets no Access-Control-Allow-Origin header
    and stays blocked (safe default while no frontend domain is known yet).
    Once ALLOWED_ORIGINS is set, only the listed origin(s) get the header.

    Reloads app.main because ALLOWED_ORIGINS is read once at import time;
    this only replaces app.main's own module-level `app`/`ALLOWED_ORIGINS`
    for this test process and does not affect the FastAPI instance other
    tests get via `from app import app` (bound once when the `app` package
    was first imported), so it can't destabilize other tests.
    """
    import importlib

    from fastapi.testclient import TestClient
    from app import main as main_module

    try:
        monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
        importlib.reload(main_module)
        assert main_module.ALLOWED_ORIGINS == []
        client = TestClient(main_module.app)
        resp = client.get("/health", headers={"Origin": "https://evil.example.com"})
        assert "access-control-allow-origin" not in {k.lower() for k in resp.headers}

        monkeypatch.setenv("ALLOWED_ORIGINS", "https://cosuma.co.kr")
        importlib.reload(main_module)
        assert main_module.ALLOWED_ORIGINS == ["https://cosuma.co.kr"]
        client2 = TestClient(main_module.app)
        allowed = client2.get("/health", headers={"Origin": "https://cosuma.co.kr"})
        assert allowed.headers.get("access-control-allow-origin") == "https://cosuma.co.kr"
        denied = client2.get("/health", headers={"Origin": "https://evil.example.com"})
        assert "access-control-allow-origin" not in {k.lower() for k in denied.headers}
    finally:
        monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
        importlib.reload(main_module)
