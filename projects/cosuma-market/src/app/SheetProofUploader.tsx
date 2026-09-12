"use client";

import { ChangeEvent, DragEvent, FormEvent, useMemo, useState } from "react";

type Issue = {
  severity?: string;
  check?: string;
  message?: string;
  sheet?: string;
  row?: number;
  column?: string;
};

type AnalysisResult = {
  filename?: string;
  issues_total?: number;
  high?: number;
  medium?: number;
  low?: number;
  preview?: Issue[];
  locked_count?: number;
  [key: string]: unknown;
};

export default function SheetProofUploader() {
  const apiUrl = process.env.NEXT_PUBLIC_SHEETPROOF_API_URL?.trim().replace(/\/+$/, "") ?? "";
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [dragging, setDragging] = useState(false);

  const previewIssues = useMemo(() => result?.preview ?? [], [result]);

  function choose(next: File | undefined) {
    if (!next) return;
    const allowed = [".xlsx", ".xlsm", ".csv"];
    const suffix = `.${next.name.split(".").pop()?.toLowerCase()}`;
    if (!allowed.includes(suffix)) { setError("XLSX, XLSM 또는 CSV 파일만 선택할 수 있습니다."); return; }
    if (next.size > 10 * 1024 * 1024) { setError("파일은 최대 10MB까지 지원합니다."); return; }
    setError(""); setResult(null); setFile(next);
  }

  function onDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault(); setDragging(false); choose(event.dataTransfer.files?.[0]);
  }

  async function downloadReport(format: "json" | "csv") {
    if (!file || !apiUrl) return;
    const response = await fetch(`${apiUrl}/api/report/${format}`, { method: "POST", body: (() => { const form = new FormData(); form.append("file", file); return form; })() });
    if (!response.ok) { setError("리포트를 다운로드하지 못했습니다."); return; }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob); const link = document.createElement("a");
    link.href = url; link.download = `${file.name.replace(/\.[^.]+$/, "")}_sheetproof.${format}`; link.click(); URL.revokeObjectURL(url);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("검사할 XLSX, XLSM 또는 CSV 파일을 선택해 주세요.");
      return;
    }

    if (!apiUrl) {
      setError("SheetProof 분석 서버가 아직 연결되지 않았습니다. 공개 배포 단계에서 분석 API를 연결합니다.");
      return;
    }

    const form = new FormData();
    form.append("file", file);

    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/analyze`, {
        method: "POST",
        body: form,
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.detail || "파일을 분석하지 못했습니다.");
      }
      setResult(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "파일 분석 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section id="analyze" className="glass rounded-[36px] p-6 md:p-10 border border-white/10">
      <div className="max-w-3xl mx-auto text-center mb-8">
        <div className="inline-flex items-center gap-2 text-xs font-bold tracking-[0.2em] text-brand uppercase mb-3"><span className="h-2 w-2 rounded-full bg-brand" /> Free check</div>
        <h2 className="text-3xl md:text-4xl font-black mb-4 tracking-tight">파일을 올리면, 검토할 곳이 보입니다</h2>
        <p className="text-gray-400 leading-relaxed">
          XLSX, XLSM, CSV 파일에서 누락값, 중복값, 형식 불일치, 계산 불일치 가능성을 자동으로 찾습니다.
        </p>
      </div>

      <form onSubmit={submit} className="max-w-2xl mx-auto space-y-5">
        <label onDragOver={(event) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={onDrop} className={`block rounded-3xl border border-dashed ${dragging ? "border-brand bg-brand/10" : "border-white/20 bg-white/[0.03]"} p-8 md:p-12 text-center cursor-pointer hover:border-brand/50 transition`}>
          <input
            type="file"
            accept=".xlsx,.xlsm,.csv"
            className="hidden"
            onChange={(event: ChangeEvent<HTMLInputElement>) => choose(event.target.files?.[0])}
          />
          <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand/15 text-2xl">⇧</div>
          <div className="font-bold text-lg mb-2">{file ? file.name : "파일을 끌어놓거나 선택하세요"}</div>
          <div className="text-xs text-gray-500">지원 형식: XLSX · XLSM · CSV <span className="mx-1 text-white/20">·</span> 최대 10MB</div>
        </label>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-5 rounded-2xl bg-brand text-black font-black text-lg disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.01] transition-transform"
        >
          {loading ? "파일을 분석하고 있습니다…" : file ? "이 파일 무료 검사하기" : "검사할 파일 선택하기"}
        </button>

        <p className="text-[11px] text-gray-500 text-center leading-relaxed">
          민감한 개인정보가 포함된 파일은 업로드하지 마세요. SheetProof의 자동 분석 결과는 검토를 돕는 참고 자료이며 모든 오류 탐지를 보장하지 않습니다.
        </p>
      </form>

      {error && (
        <div className="max-w-2xl mx-auto mt-6 rounded-2xl border border-red-400/20 bg-red-400/5 p-4 text-sm text-red-200">
          {error}
        </div>
      )}

      {result && (
        <div className="max-w-3xl mx-auto mt-8 space-y-5">
          <div className="flex items-center justify-between gap-4 mb-3"><div><p className="text-xs uppercase tracking-[.18em] text-brand font-bold">Analysis result</p><p className="text-sm text-gray-400 mt-1">{result.filename ?? file?.name}</p></div><span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">검사 완료</span></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Metric label="전체 문제" value={result.issues_total ?? 0} />
            <Metric label="HIGH" value={result.high ?? 0} />
            <Metric label="MEDIUM" value={result.medium ?? 0} />
            <Metric label="LOW" value={result.low ?? 0} />
          </div>
          {previewIssues.length > 0 && (
            <div className="rounded-3xl border border-white/10 overflow-hidden">
              {previewIssues.map((issue, index) => (
                <div key={`${issue.sheet}-${issue.row}-${index}`} className="p-4 border-b last:border-b-0 border-white/10 bg-black/10">
                  <div className="flex flex-wrap gap-2 items-center text-xs text-gray-500 mb-2">
                    <span className="font-bold text-brand">{issue.severity?.toUpperCase() ?? "CHECK"}</span>
                    {issue.sheet && <span>{issue.sheet}</span>}
                    {issue.row != null && <span>{issue.row}행</span>}
                    {issue.column && <span>{issue.column}열</span>}
                  </div>
                  <p className="text-sm text-gray-200">{issue.message ?? issue.check ?? "검토가 필요한 항목입니다."}</p>
                </div>
              ))}
            </div>
          )}
          {(result.locked_count ?? 0) > 0 && (
            <p className="text-sm text-gray-400">현재 화면에는 {previewIssues.length}건의 미리보기를 표시합니다. 나머지 {result.locked_count}건은 이 화면에 표시되지 않습니다.</p>
          )}
          <div className="flex flex-col sm:flex-row gap-3 pt-2"><button type="button" onClick={() => downloadReport("csv")} className="flex-1 rounded-2xl border border-white/15 px-4 py-3 text-sm font-bold hover:bg-white/5 transition">CSV 전체 리포트 다운로드</button><button type="button" onClick={() => downloadReport("json")} className="flex-1 rounded-2xl border border-white/15 px-4 py-3 text-sm font-bold hover:bg-white/5 transition">JSON 전체 리포트 다운로드</button></div>
        </div>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl bg-white/[0.04] border border-white/10 p-4 text-center">
      <div className="text-2xl font-black">{value}</div>
      <div className="text-[11px] text-gray-500 mt-1">{label}</div>
    </div>
  );
}
