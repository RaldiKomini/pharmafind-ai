import { useState } from "react";
import { Beaker, Radar, Sparkles, TrendingUp } from "lucide-react";
import { Card, CardBody, CardHeader, CardSubtle, CardTitle } from "../common/Card";
import { ErrorAlert } from "../common/ErrorAlert";
import { Badge } from "../common/Badge";
import { ReviewForm } from "./ReviewForm";
import { SummaryCards } from "./SummaryCards";
import { SignalsTable } from "./SignalsTable";
import { SignalDetailsModal } from "./SignalDetailsModal";
import { MarkdownReportViewer } from "./MarkdownReportViewer";
import {
  ApiError,
  downloadReviewPdf,
  runReview,
  triggerBlobDownload,
} from "../../lib/api";
import type {
  SafetyReviewRequest,
  SafetyReviewResponse,
  SafetySignal,
} from "../../lib/types";
import { isLlmCreditError } from "../../lib/utils";

const DEFAULT_REQUEST: SafetyReviewRequest = {
  drug_name: "Ozempic",
  recent_days: 90,
  baseline_days: 365,
  max_reports_per_window: 1000,
  max_signals: 20,
  max_pubmed_papers_per_signal: 5,
  use_llm: false,
};

interface Props {
  backendOnline: boolean;
}

export function ReviewMode({ backendOnline }: Props) {
  const [request, setRequest] = useState<SafetyReviewRequest>(DEFAULT_REQUEST);
  const [loading, setLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [result, setResult] = useState<SafetyReviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const [selectedSignal, setSelectedSignal] = useState<SafetySignal | null>(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setWarning(null);
    setPdfError(null);
    try {
      const data = await runReview(request);
      setResult(data);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : (e as Error).message;
      if (request.use_llm && isLlmCreditError(msg)) {
        setWarning(
          "LLM-enhanced narrative failed (likely missing OpenAI API key, credits, or rate limit). Try again with the LLM toggle disabled to run deterministic review only."
        );
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    setPdfLoading(true);
    setPdfError(null);
    try {
      const blob = await downloadReviewPdf(request);
      const safeName = request.drug_name.trim().toLowerCase().replace(/\s+/g, "_");
      triggerBlobDownload(blob, `${safeName || "review"}_safety_review.pdf`);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : (e as Error).message;
      setPdfError(
        `PDF generation failed: ${msg}. Your existing review results are still available.`
      );
    } finally {
      setPdfLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
      {/* Left: form */}
      <div className="lg:col-span-4 space-y-5">
        <Card glass>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Beaker className="h-4 w-4 text-brand-600" />
                  Deterministic Review
                </CardTitle>
                <CardSubtle>Configure the signal-detection run</CardSubtle>
              </div>
              <Badge tone="info" dot>FAERS + PubMed</Badge>
            </div>
          </CardHeader>
          <CardBody>
            <ReviewForm
              value={request}
              onChange={setRequest}
              onSubmit={handleRun}
              loading={loading}
              disabled={!backendOnline}
            />
          </CardBody>
        </Card>

        <Card>
          <CardBody className="pt-5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5 text-violet-500" />
              How signals are scored
            </h4>
            <ul className="text-xs text-slate-600 space-y-1.5 leading-relaxed">
              <li>• Compares recent reaction frequency to baseline window</li>
              <li>• Flags patterns exceeding ratio + score thresholds</li>
              <li>• Searches PubMed for supporting literature</li>
              <li>• Grades evidence: none → weak → moderate → strong</li>
            </ul>
          </CardBody>
        </Card>
      </div>

      {/* Right: results */}
      <div className="lg:col-span-8 space-y-5 min-w-0">
        {error && <ErrorAlert title="Review failed" message={error} onClose={() => setError(null)} />}
        {warning && (
          <ErrorAlert
            tone="warning"
            title="LLM narrative unavailable"
            message={warning}
            onClose={() => setWarning(null)}
          />
        )}
        {pdfError && (
          <ErrorAlert
            tone="warning"
            title="PDF download failed"
            message={pdfError}
            onClose={() => setPdfError(null)}
          />
        )}

        {!result && !loading && <EmptyState />}

        {loading && (
          <Card>
            <CardBody className="py-16 text-center">
              <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-br from-brand-500 to-teal-500 flex items-center justify-center pulse-dot">
                <Radar className="h-6 w-6 text-white" />
              </div>
              <p className="mt-3 text-sm font-medium text-slate-800">Aggregating FAERS reports…</p>
              <p className="text-xs text-slate-500">Comparing patterns and searching PubMed.</p>
            </CardBody>
          </Card>
        )}

        {result && (
          <>
            <SummaryCards summary={result.summary} />
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-amber-600" />
                      Flagged reporting signals
                    </CardTitle>
                    <CardSubtle>Patterns for human review · not causal claims</CardSubtle>
                  </div>
                  <Badge tone="warning">{result.summary.signals?.length ?? 0} signals</Badge>
                </div>
              </CardHeader>
              <CardBody>
                <SignalsTable
                  signals={result.summary.signals ?? []}
                  onSelect={setSelectedSignal}
                />
              </CardBody>
            </Card>

            <MarkdownReportViewer
              markdown={result.markdown_report}
              onDownloadPdf={handleDownloadPdf}
              pdfLoading={pdfLoading}
              pdfDisabled={!backendOnline}
            />
          </>
        )}
      </div>

      <SignalDetailsModal signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </div>
  );
}

function EmptyState() {
  return (
    <Card>
      <CardBody className="py-14 text-center">
        <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-br from-brand-100 to-teal-100 flex items-center justify-center ring-1 ring-brand-200/60">
          <Beaker className="h-6 w-6 text-brand-600" />
        </div>
        <h3 className="mt-3 text-sm font-semibold text-slate-900">Ready to review</h3>
        <p className="mx-auto mt-1 max-w-md text-xs text-slate-500 leading-relaxed">
          Enter a drug name and run a deterministic review. Results, flagged signals, and a
          formatted brief will appear here.
        </p>
      </CardBody>
    </Card>
  );
}
