from __future__ import annotations

import io
import json
import math
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.concurrency import run_in_threadpool

BASE_DIR = Path(__file__).resolve().parent
APP_VERSION = "0.3.0-pre"
app = FastAPI(title="SheetProof", version=APP_VERSION)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def parse_allowed_origins(raw: str | None) -> list[str]:
    """Parse a comma-separated ALLOWED_ORIGINS value into a clean origin list.

    Blank/whitespace entries are dropped. An unset or empty value yields an
    empty list, which means no CORS middleware is installed at all (browser
    cross-origin requests stay blocked) -- the safe default when the actual
    frontend domain isn't known/configured yet.
    """
    if not raw:
        return []
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


# The site (e.g. a Next.js frontend on Vercel) and this API are expected to
# be served from different origins, so the browser will block fetch() calls
# from the site to this API unless it's explicitly allowlisted here. Set
# ALLOWED_ORIGINS to a comma-separated list of the exact origins that should
# be allowed to call this API, e.g.:
#   ALLOWED_ORIGINS=https://cosuma.co.kr,https://sheetproof-git-preview.vercel.app
ALLOWED_ORIGINS = parse_allowed_origins(os.environ.get("ALLOWED_ORIGINS"))
if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        allow_credentials=False,
    )

env = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_ROWS = 100_000
SUPPORTED_SUFFIXES = {".csv", ".xlsx", ".xlsm"}

ID_HINTS = ("id", "sku", "code", "key", "번호", "코드", "아이디", "상품코드")
QTY_HINTS = ("qty", "quantity", "수량", "개수")
PRICE_HINTS = ("unit price", "unit_price", "price", "단가", "가격")
AMOUNT_HINTS = ("amount", "total", "subtotal", "합계", "금액", "총액")
DATE_HINTS = ("date", "day", "일자", "날짜")

# Compound Korean terms that contain an ID_HINTS substring (번호) but name a
# non-unique attribute rather than an identifier/key column. Without this,
# '전화번호'/'우편번호' get treated as ID/SKU-style columns and their (normal,
# expected) repeated values get reported as duplicate-key violations.
# Genuine identifiers like '주문번호'/'사업자번호'/'품목코드' are unaffected
# since they are not in this list.
ID_HINT_EXCLUSIONS = ("전화번호", "휴대폰번호", "핸드폰번호", "팩스번호", "우편번호")


def norm_name(name: Any) -> str:
    return re.sub(r"\s+", " ", str(name).strip().lower())


_HAS_HANGUL = re.compile(r"[가-힣]")


def has_hint(name: Any, hints: tuple[str, ...], *, exclusions: tuple[str, ...] = ()) -> bool:
    """Match column hints against a column name.

    Korean hints match as a substring of the whole (space-stripped) name,
    because Korean compound column names are conventionally written without
    separators (e.g. '판매단가' contains '단가', '출고수량' contains '수량').
    Latin-alphabet hints require an exact token match instead of a substring
    match, because arbitrary substring matching false-positives on unrelated
    English words that happen to contain the hint (e.g. 'code' inside
    'postcode'/'zipcode', 'key' inside 'keyword').

    `exclusions` lists whole compound terms that must never match even
    though they contain a hint substring (e.g. '전화번호'/'우편번호' contain
    '번호' but are not identifier columns, unlike '주문번호'/'사업자번호').
    """
    n = norm_name(name).replace("_", " ").replace("-", " ")
    n_nospace = n.replace(" ", "")
    for exclusion in exclusions:
        ex = norm_name(exclusion).replace("_", " ").replace(" ", "")
        if ex and ex in n_nospace:
            return False
    tokens = [t for t in re.split(r"[^0-9a-zA-Z가-힣]+", n) if t]
    for hint in hints:
        h = norm_name(hint).replace("_", " ")
        if not h:
            continue
        if " " in h:
            if h in n:
                return True
        elif _HAS_HANGUL.search(h):
            if h in n:
                return True
        elif h in tokens:
            return True
    return False


def _read_csv(raw: bytes) -> pd.DataFrame:
    bio = io.BytesIO(raw)
    last_exc: Exception | None = None
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            bio.seek(0)
            return pd.read_csv(bio, encoding=enc)
        except UnicodeDecodeError as exc:
            last_exc = exc
        except Exception:
            bio.seek(0)
            try:
                return pd.read_csv(bio, encoding=enc, engine="python")
            except Exception as exc:
                last_exc = exc
    raise last_exc or ValueError("CSV를 읽을 수 없습니다.")


def _looks_like_title_row(columns: list[Any]) -> bool:
    """Detect pandas' auto-generated 'Unnamed: N' column names, which mean
    the row pandas used as the header was actually a title/banner row (a
    common pattern in Korean business templates: row 1 = report title in a
    merged cell, row 2 = the real column headers)."""
    if len(columns) < 2:
        return False
    unnamed = sum(1 for c in columns if str(c).startswith("Unnamed:"))
    return (unnamed / len(columns)) > 0.5


_ALL_COLUMN_HINTS = ID_HINTS + QTY_HINTS + PRICE_HINTS + AMOUNT_HINTS + DATE_HINTS


def _header_hint_score(columns: list[Any]) -> int:
    """Count how many column names look like a recognized business-data
    header (matches a known ID/QTY/PRICE/AMOUNT/DATE hint). Used as
    corroborating evidence for whether a row is a real header row, since a
    mostly-'Unnamed:' row alone is not enough: a genuinely sparse header
    (e.g. only the first column named, the rest blank) produces the exact
    same 'Unnamed:' ratio as an actual title/banner row."""
    return sum(1 for c in columns if has_hint(c, _ALL_COLUMN_HINTS))


def read_workbook(filename: str, raw: bytes) -> dict[str, pd.DataFrame]:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise HTTPException(status_code=400, detail="현재 CSV, XLSX, XLSM 파일만 지원합니다.")
    if not raw:
        raise HTTPException(status_code=400, detail="빈 파일은 분석할 수 없습니다.")

    try:
        if suffix == ".csv":
            return {"CSV": _read_csv(raw)}
        excel_file = pd.ExcelFile(io.BytesIO(raw), engine="openpyxl")
        if not excel_file.sheet_names:
            raise ValueError("워크북에 읽을 수 있는 시트가 없습니다.")
        sheets: dict[str, pd.DataFrame] = {}
        for name in excel_file.sheet_names:
            df = excel_file.parse(sheet_name=name)
            header_row_offset = 0
            if _looks_like_title_row(list(df.columns)):
                retry = excel_file.parse(sheet_name=name, header=1)
                original_score = _header_hint_score(list(df.columns))
                retry_score = _header_hint_score(list(retry.columns))
                # Require the retried header to look MORE like a real header
                # than the current one (matches at least one known business
                # column term, and more than the current row does) before
                # discarding the current row. A sparse-but-real header (e.g.
                # only the first column named) produces the same 'Unnamed:'
                # ratio as a genuine title row, so the 'Unnamed:' ratio alone
                # is not enough evidence — without this check, a normal file
                # with a sparse header would have its real header row
                # replaced by its own first data row. When it's ambiguous,
                # stay conservative and keep header=0.
                if (
                    not _looks_like_title_row(list(retry.columns))
                    and retry_score > 0
                    and retry_score > original_score
                ):
                    df = retry
                    header_row_offset = 1
            # Stashed so analyze() can report spreadsheet-accurate row numbers
            # even when the real header was not on the first row.
            df.attrs["header_row_offset"] = header_row_offset
            sheets[str(name)] = df
        return sheets
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"파일을 읽지 못했습니다: {exc}") from exc


def read_upload(filename: str, raw: bytes) -> pd.DataFrame:
    """Backward-compatible helper returning the first sheet only."""
    return next(iter(read_workbook(filename, raw).values()))


def safe_value(v: Any) -> str:
    if pd.isna(v):
        return "(빈 값)"
    s = str(v)
    return s if len(s) <= 120 else s[:117] + "..."


def add_issue(
    issues: list[dict[str, Any]],
    *,
    severity: str,
    check: str,
    message: str,
    row: int | None = None,
    column: str | None = None,
    value: Any = None,
    suggestion: str | None = None,
) -> None:
    issues.append({
        "severity": severity,
        "check": check,
        "message": message,
        "row": row,
        "column": column,
        "value": safe_value(value) if value is not None else None,
        "suggestion": suggestion,
    })


def detect_required_blanks(df: pd.DataFrame, issues: list[dict[str, Any]]) -> None:
    if df.empty:
        return
    for col in df.columns:
        non_null_ratio = df[col].notna().mean()
        if 0.85 <= non_null_ratio < 1:
            missing_idx = df.index[df[col].isna()].tolist()
            for idx in missing_idx[:50]:
                add_issue(
                    issues,
                    severity="high",
                    check="필수값 누락",
                    message=f"'{col}' 열은 대부분 채워져 있지만 이 행만 비어 있습니다.",
                    row=int(idx) + 2,
                    column=str(col),
                    suggestion="원본 자료에서 값을 확인하거나, 의도된 공란인지 규칙으로 명시하세요.",
                )


def detect_duplicates(df: pd.DataFrame, issues: list[dict[str, Any]]) -> None:
    dup_mask = df.duplicated(keep=False)
    for idx in df.index[dup_mask].tolist()[:30]:
        add_issue(
            issues,
            severity="medium",
            check="중복 행",
            message="완전히 동일한 행이 두 번 이상 존재합니다.",
            row=int(idx) + 2,
            suggestion="실제 중복 레코드인지 확인한 뒤 하나만 남기세요.",
        )

    for col in df.columns:
        if has_hint(col, ID_HINTS, exclusions=ID_HINT_EXCLUSIONS):
            s = df[col].dropna().astype(str).str.strip()
            dup_values = s[s.duplicated(keep=False)]
            for val, count in Counter(dup_values).most_common(20):
                rows = (df.index[df[col].astype(str).str.strip() == val] + 2).tolist()
                add_issue(
                    issues,
                    severity="high",
                    check="중복 키",
                    message=f"'{col}' 값 '{val}'이(가) {count}번 반복됩니다. 행: {rows[:8]}",
                    column=str(col),
                    value=val,
                    suggestion="ID/SKU/코드는 보통 고유값이어야 합니다. 중복 원인을 확인하세요.",
                )


def classify_value(v: Any) -> str:
    if pd.isna(v) or str(v).strip() == "":
        return "blank"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return "number"
    s = str(v).strip()
    ns = re.sub(r"[,$₩€£¥\s]", "", s)
    try:
        float(ns)
        return "number_text"
    except ValueError:
        pass
    if re.fullmatch(r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}", s) or re.fullmatch(r"\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}", s):
        return "date_text"
    return "text"


def detect_mixed_types(df: pd.DataFrame, issues: list[dict[str, Any]]) -> None:
    for col in df.columns:
        vals = [(idx, v, classify_value(v)) for idx, v in df[col].items() if not pd.isna(v) and str(v).strip() != ""]
        if len(vals) < 4:
            continue
        families = []
        for _, _, t in vals:
            if t in ("number", "number_text"):
                families.append("number")
            elif t == "date_text":
                families.append("date")
            else:
                families.append("text")
        counts = Counter(families)
        dominant, dominant_count = counts.most_common(1)[0]
        if dominant_count / len(families) >= 0.75 and len(counts) > 1:
            bad_family = [fam for fam in counts if fam != dominant]
            for idx, v, t in vals:
                fam = "number" if t in ("number", "number_text") else ("date" if t == "date_text" else "text")
                if fam in bad_family:
                    add_issue(
                        issues,
                        severity="medium",
                        check="열 데이터 타입 불일치",
                        message=f"'{col}' 열은 대부분 {dominant} 형식인데 이 값은 {fam} 형식입니다.",
                        row=int(idx) + 2,
                        column=str(col),
                        value=v,
                        suggestion="열의 데이터 형식을 하나로 통일하세요.",
                    )


def detect_numeric_format_issues(df: pd.DataFrame, issues: list[dict[str, Any]]) -> None:
    numeric_name_hints = QTY_HINTS + PRICE_HINTS + AMOUNT_HINTS
    for col in df.columns:
        s = df[col].dropna()
        if len(s) < 4:
            continue
        cleaned = (s.astype(str)
                     .str.replace(",", "", regex=False)
                     .str.replace("₩", "", regex=False)
                     .str.replace("$", "", regex=False)
                     .str.replace("€", "", regex=False)
                     .str.replace("£", "", regex=False)
                     .str.replace("¥", "", regex=False)
                     .str.strip())
        converted = pd.to_numeric(cleaned, errors="coerce")
        ratio = converted.notna().mean()
        likely_numeric = pd.api.types.is_numeric_dtype(df[col]) or has_hint(col, numeric_name_hints) or ratio >= 0.80
        if likely_numeric and 0 < ratio < 1:
            bad = converted[converted.isna()].index.tolist()
            for idx in bad[:30]:
                if any(i.get("check") == "열 데이터 타입 불일치" and i.get("row") == int(idx) + 2 and i.get("column") == str(col) for i in issues):
                    continue
                add_issue(
                    issues,
                    severity="medium",
                    check="숫자 형식 오류",
                    message=f"'{col}' 열은 숫자 열로 보이지만 이 값은 숫자로 해석되지 않습니다.",
                    row=int(idx) + 2,
                    column=str(col),
                    value=df.at[idx, col],
                    suggestion="통화기호·공백·문자 또는 잘못된 소수점 표기를 확인하세요.",
                )


def date_pattern(s: str) -> str | None:
    s = s.strip()
    patterns = [
        (r"\d{4}-\d{1,2}-\d{1,2}", "YYYY-MM-DD"),
        (r"\d{4}/\d{1,2}/\d{1,2}", "YYYY/MM/DD"),
        (r"\d{4}\.\d{1,2}\.\d{1,2}", "YYYY.MM.DD"),
        (r"\d{1,2}/\d{1,2}/\d{4}", "MM/DD/YYYY"),
        (r"\d{1,2}-\d{1,2}-\d{4}", "MM-DD-YYYY"),
    ]
    for pat, name in patterns:
        if re.fullmatch(pat, s):
            return name
    return None


def detect_date_format_mix(df: pd.DataFrame, issues: list[dict[str, Any]]) -> None:
    for col in df.columns:
        vals = [(idx, str(v).strip(), date_pattern(str(v))) for idx, v in df[col].dropna().items()]
        date_vals = [(idx, v, p) for idx, v, p in vals if p]
        if len(date_vals) < 3 and not has_hint(col, DATE_HINTS):
            continue
        patterns = Counter(p for _, _, p in date_vals if p)
        if len(patterns) > 1:
            dominant = patterns.most_common(1)[0][0]
            for idx, v, p in date_vals:
                if p != dominant:
                    add_issue(
                        issues,
                        severity="low",
                        check="날짜 형식 혼용",
                        message=f"'{col}' 열의 날짜 형식이 섞여 있습니다. 주 형식은 {dominant}, 이 값은 {p}입니다.",
                        row=int(idx) + 2,
                        column=str(col),
                        value=v,
                        suggestion=f"날짜 표시 형식을 {dominant}처럼 하나로 통일하세요.",
                    )


def pick_column(columns: list[Any], hints: tuple[str, ...]) -> Any | None:
    for col in columns:
        if has_hint(col, hints):
            return col
    return None


def to_num(v: Any) -> float | None:
    if pd.isna(v):
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = re.sub(r"[,$₩€£¥\s]", "", str(v))
    try:
        return float(s)
    except ValueError:
        return None


def detect_arithmetic(df: pd.DataFrame, issues: list[dict[str, Any]]) -> None:
    qty_col = pick_column(list(df.columns), QTY_HINTS)
    price_col = pick_column(list(df.columns), PRICE_HINTS)
    amount_col = pick_column(list(df.columns), AMOUNT_HINTS)
    if not all((qty_col, price_col, amount_col)):
        return
    for idx, row in df.iterrows():
        q, p, a = to_num(row[qty_col]), to_num(row[price_col]), to_num(row[amount_col])
        if q is None or p is None or a is None:
            continue
        expected = q * p
        tol = max(0.01, abs(expected) * 0.001)
        if not math.isclose(expected, a, rel_tol=0.001, abs_tol=tol):
            add_issue(
                issues,
                severity="high",
                check="산술 불일치",
                message=f"{qty_col} × {price_col} 값이 {amount_col}와 일치하지 않습니다.",
                row=int(idx) + 2,
                column=str(amount_col),
                value=row[amount_col],
                suggestion=f"예상 금액은 {expected:,.2f} 입니다. 원본 수량·단가·금액을 확인하세요.",
            )


def analyze(df: pd.DataFrame, *, sheet: str | None = None, include_all: bool = False) -> dict[str, Any]:
    # Read before .copy(): a header row skipped during reading (see
    # read_workbook/_looks_like_title_row) shifts every data row down by
    # that many spreadsheet rows, so reported row numbers must be shifted
    # back to match what the user actually sees in the file.
    header_row_offset = int(df.attrs.get("header_row_offset", 0))
    df = df.copy()
    df.columns = [str(c).strip() if str(c).strip() else f"Unnamed_{i+1}" for i, c in enumerate(df.columns)]
    issues: list[dict[str, Any]] = []
    detect_required_blanks(df, issues)
    detect_duplicates(df, issues)
    detect_mixed_types(df, issues)
    detect_numeric_format_issues(df, issues)
    detect_date_format_mix(df, issues)
    detect_arithmetic(df, issues)

    for issue in issues:
        issue["sheet"] = sheet
        if header_row_offset and issue.get("row") is not None:
            issue["row"] += header_row_offset

    severity_order = {"high": 0, "medium": 1, "low": 2}
    issues.sort(key=lambda x: (severity_order.get(x["severity"], 9), x.get("row") or 10**9))
    counts = Counter(i["severity"] for i in issues)
    result = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "issues_total": len(issues),
        "high": counts.get("high", 0),
        "medium": counts.get("medium", 0),
        "low": counts.get("low", 0),
        "preview": issues[:3],
        "locked_count": max(0, len(issues) - 3),
        "checks": [
            "필수값 누락", "중복 행/ID/SKU", "열 데이터 타입 불일치",
            "숫자 형식 오류", "날짜 형식 혼용", "수량×단가=금액 산술 검증"
        ],
    }
    if include_all:
        result["all_issues"] = issues
    return result


def analyze_workbook(sheets: dict[str, pd.DataFrame], *, include_all: bool = False) -> dict[str, Any]:
    all_issues: list[dict[str, Any]] = []
    total_rows = 0
    total_columns = 0
    sheet_summaries: list[dict[str, Any]] = []

    for sheet_name, df in sheets.items():
        r = analyze(df, sheet=sheet_name, include_all=True)
        total_rows += r["rows"]
        total_columns += r["columns"]
        all_issues.extend(r["all_issues"])
        sheet_summaries.append({
            "sheet": sheet_name,
            "rows": r["rows"],
            "columns": r["columns"],
            "issues_total": r["issues_total"],
        })

    severity_order = {"high": 0, "medium": 1, "low": 2}
    all_issues.sort(key=lambda x: (
        severity_order.get(x["severity"], 9),
        x.get("sheet") or "",
        x.get("row") or 10**9,
    ))
    counts = Counter(i["severity"] for i in all_issues)
    result: dict[str, Any] = {
        "rows": total_rows,
        "columns": total_columns,
        "sheets": len(sheets),
        "sheet_summaries": sheet_summaries,
        "issues_total": len(all_issues),
        "high": counts.get("high", 0),
        "medium": counts.get("medium", 0),
        "low": counts.get("low", 0),
        "preview": all_issues[:3],
        "locked_count": max(0, len(all_issues) - 3),
        "checks": [
            "필수값 누락", "중복 행/ID/SKU", "열 데이터 타입 불일치",
            "숫자 형식 오류", "날짜 형식 혼용", "수량×단가=금액 산술 검증"
        ],
    }
    if include_all:
        result["all_issues"] = all_issues
    return result


def validate_upload(file: UploadFile, raw: bytes) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일명이 없습니다.")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise HTTPException(status_code=400, detail="현재 CSV, XLSX, XLSM 파일만 지원합니다.")
    if not raw:
        raise HTTPException(status_code=400, detail="빈 파일은 분석할 수 없습니다.")
    if len(raw) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="파일은 최대 10MB까지 지원합니다.")


def load_and_analyze(file: UploadFile, raw: bytes, *, include_all: bool = False) -> dict[str, Any]:
    validate_upload(file, raw)
    sheets = read_workbook(file.filename or "", raw)
    total_rows = sum(len(df) for df in sheets.values())
    if total_rows > MAX_ROWS:
        raise HTTPException(status_code=413, detail=f"현재 MVP는 전체 시트 합산 최대 {MAX_ROWS:,}행까지 지원합니다.")
    result = analyze_workbook(sheets, include_all=include_all)
    result["filename"] = file.filename
    return result


@app.get("/", response_class=HTMLResponse)
async def home() -> HTMLResponse:
    template = env.get_template("index.html")
    return HTMLResponse(template.render())


_CSV_FORMULA_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")


def csv_safe(v: Any) -> Any:
    """Neutralize CSV/formula injection (CWE-1236).

    Sheet names, column headers, and cell values in a report all originate
    from an untrusted uploaded file. If any of them start with '=', '+',
    '-', or '@', spreadsheet software (Excel/LibreOffice) will treat that
    cell as a formula when the downloaded report is opened, which can run
    arbitrary formulas (e.g. HYPERLINK-based phishing or, on older Excel/
    ODBC setups, command execution) against whoever opens the report.
    Prefixing with a single quote forces the cell to be treated as text.
    """
    if pd.isna(v):
        return v
    s = str(v)
    if s.startswith(_CSV_FORMULA_TRIGGERS):
        return "'" + s
    return s


@app.post("/api/analyze")
async def api_analyze(file: UploadFile = File(...)) -> dict[str, Any]:
    raw = await file.read()
    # Parsing/analysis is synchronous CPU-bound pandas/openpyxl work; running
    # it directly in this coroutine would block the single asyncio event
    # loop (and therefore every other concurrent request) for the whole
    # duration of a large-but-legal upload. Offload it to a worker thread.
    return await run_in_threadpool(load_and_analyze, file, raw)


@app.post("/api/report/json")
async def api_report_json(file: UploadFile = File(...)) -> Response:
    raw = await file.read()
    result = await run_in_threadpool(load_and_analyze, file, raw, include_all=True)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    stem = Path(file.filename or "sheetproof").stem
    return Response(
        content=payload,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{stem}_sheetproof.json"'},
    )


@app.post("/api/report/csv")
async def api_report_csv(file: UploadFile = File(...)) -> Response:
    raw = await file.read()
    result = await run_in_threadpool(load_and_analyze, file, raw, include_all=True)
    columns = ["severity", "check", "sheet", "row", "column", "value", "message", "suggestion"]
    report_df = pd.DataFrame(result["all_issues"], columns=columns)
    for col in ("sheet", "column", "value", "message", "suggestion"):
        report_df[col] = report_df[col].map(csv_safe)
    csv_bytes = report_df.to_csv(index=False).encode("utf-8-sig")
    stem = Path(file.filename or "sheetproof").stem
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{stem}_sheetproof.csv"'},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": APP_VERSION}
