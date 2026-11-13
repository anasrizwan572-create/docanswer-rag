'use client';

import React, { useState } from 'react';
import { 
  Search, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  ExternalLink, 
  ShieldCheck, 
  HelpCircle, 
  ChevronRight,
  BookOpen,
  Sparkles,
  Info
} from 'lucide-react';

interface Citation {
  id: number;
  source: string;
  page: number;
  section: string;
  passage_text: string;
  score: number;
}

interface QueryResponse {
  answer: string;
  citations: Citation[];
  confidence: 'high' | 'medium' | 'low';
  found: boolean;
}

const EXAMPLE_QUESTIONS = [
  "What is the 401(k) company match and vesting schedule?",
  "How much is the one-time home office setup allowance?",
  "Can an employee on probation take discretionary annual leave?",
  "When is a medical certificate required for sick leave absences?",
  "What is the reimbursement limit for pet health insurance?"
];

export default function Home() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeCitationId, setActiveCitationId] = useState<number | null>(null);

  const handleQuery = async (queryText: string) => {
    const q = queryText.trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    setResponse(null);
    setActiveCitationId(null);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server responded with error status ${res.status}`);
      }

      const data: QueryResponse = await res.json();
      setResponse(data);
      if (data.citations && data.citations.length > 0) {
        setActiveCitationId(data.citations[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to query document. Please verify connection.');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleQuery(question);
  };

  const renderFormattedAnswer = (text: string) => {
    // Splits on [1], [2], etc. to make them interactive clickable pills
    const parts = text.split(/(\[\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const citId = parseInt(match[1], 10);
        const isActive = activeCitationId === citId;
        return (
          <button
            key={i}
            onClick={() => setActiveCitationId(citId)}
            className={`inline-flex items-center px-1.5 py-0.5 mx-0.5 text-xs font-semibold rounded transition-colors ${
              isActive
                ? 'bg-sky-600 text-white ring-2 ring-sky-300 shadow-sm'
                : 'bg-sky-100 text-sky-800 hover:bg-sky-200'
            }`}
            title={`View Source Citation [${citId}]`}
          >
            [{citId}]
          </button>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* Top Header */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-30 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 bg-sky-700 rounded-lg flex items-center justify-center text-white shadow-xs">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold tracking-tight text-slate-900">DocAnswer</span>
                <span className="text-xs font-medium uppercase tracking-wider bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">
                  RAG Assistant
                </span>
              </div>
              <p className="text-xs text-slate-500">Enterprise Verified Document Intelligence</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="hidden sm:flex items-center space-x-2 text-xs text-slate-600 bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5">
              <BookOpen className="h-3.5 w-3.5 text-sky-700" />
              <span className="font-medium text-slate-700">Acme Technologies HR Handbook</span>
              <span className="text-slate-400">|</span>
              <span>16 Pages (75 Chunks)</span>
            </div>
            <div className="flex items-center space-x-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Index Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* Trust & Legal Disclaimer Bar */}
      <div className="bg-amber-50/80 border-b border-amber-200/60 px-4 py-2 text-center text-xs text-amber-800 flex items-center justify-center space-x-1.5">
        <Info className="h-3.5 w-3.5 flex-shrink-0 text-amber-700" />
        <span>
          <strong>Disclaimer:</strong> Verify important decisions against the original document. Answers are strictly constrained to indexed passages with inline citations.
        </span>
      </div>

      {/* Main Content Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left / Center Query Column (7 cols) */}
          <section className="lg:col-span-7 flex flex-col space-y-5">
            {/* Question Input Card */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
              <form onSubmit={onSubmit} className="space-y-3">
                <label htmlFor="question-input" className="block text-sm font-semibold text-slate-800">
                  Ask a question about the HR Policy:
                </label>
                <div className="relative">
                  <textarea
                    id="question-input"
                    rows={3}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value.slice(0, 500))}
                    placeholder="e.g., What is the 401(k) company match and vesting schedule?"
                    className="w-full rounded-lg border border-slate-300 p-3 text-sm text-slate-900 focus:border-sky-500 focus:ring-2 focus:ring-sky-200 focus:outline-none transition resize-none pr-10"
                    disabled={loading}
                  />
                  <div className="absolute right-3 bottom-3 text-xs text-slate-400">
                    {question.length}/500
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-xs text-slate-500 flex items-center gap-1">
                    <Sparkles className="h-3.5 w-3.5 text-sky-600" /> Hybrid Dense + BM25 Retrieval
                  </span>
                  <button
                    type="submit"
                    disabled={loading || !question.trim()}
                    className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-sky-700 text-white text-sm font-medium hover:bg-sky-800 disabled:opacity-50 disabled:cursor-not-allowed shadow-xs transition"
                  >
                    {loading ? (
                      <>
                        <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Retrieving...</span>
                      </>
                    ) : (
                      <>
                        <Search className="h-4 w-4" />
                        <span>Ask DocAnswer</span>
                      </>
                    )}
                  </button>
                </div>
              </form>

              {/* Sample Question Chips */}
              <div className="mt-4 pt-4 border-t border-slate-100">
                <p className="text-xs font-medium text-slate-500 mb-2">Try an example question:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_QUESTIONS.map((eq, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuestion(eq);
                        handleQuery(eq);
                      }}
                      disabled={loading}
                      className="text-xs text-left bg-slate-100 hover:bg-sky-50 hover:text-sky-800 border border-slate-200 rounded-md px-2.5 py-1.5 transition text-slate-700"
                    >
                      {eq}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start space-x-3 text-red-800">
                <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <strong className="font-semibold">Query Error:</strong> {error}
                </div>
              </div>
            )}

            {/* Loading State Skeleton */}
            {loading && (
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4 animate-pulse">
                <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-slate-200 rounded w-full"></div>
                  <div className="h-4 bg-slate-200 rounded w-5/6"></div>
                  <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                </div>
                <div className="pt-2 flex items-center space-x-2 text-xs text-sky-700 font-medium">
                  <div className="h-3 w-3 bg-sky-600 rounded-full animate-ping"></div>
                  <span>Searching dense embeddings & BM25 indices...</span>
                </div>
              </div>
            )}

            {/* Answer Display */}
            {response && !loading && (
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="h-5 w-5 text-sky-700" />
                    <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
                      DocAnswer Synthesis
                    </h2>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-slate-500">Confidence:</span>
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded capitalize ${
                      response.confidence === 'high' 
                        ? 'bg-emerald-100 text-emerald-800' 
                        : response.confidence === 'medium'
                        ? 'bg-sky-100 text-sky-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}>
                      {response.confidence}
                    </span>
                  </div>
                </div>

                {response.found ? (
                  <div className="prose prose-sm max-w-none text-slate-800 leading-relaxed text-sm">
                    {renderFormattedAnswer(response.answer)}
                  </div>
                ) : (
                  /* Refusal / Not Found State */
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-2">
                    <div className="flex items-center space-x-2 text-amber-800 font-semibold text-sm">
                      <AlertTriangle className="h-4 w-4 text-amber-600" />
                      <span>Not Found in Documents</span>
                    </div>
                    <p className="text-sm text-amber-900 font-medium">
                      "{response.answer}"
                    </p>
                    <p className="text-xs text-amber-700">
                      DocAnswer enforces strict zero-hallucination constraints. If a policy or benefit is not explicitly articulated in the indexed documents, the assistant will refuse rather than fabricate assumptions.
                    </p>
                  </div>
                )}

                {response.found && response.citations.length > 0 && (
                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <span>
                      {response.citations.length} verified passage{response.citations.length > 1 ? 's' : ''} cited.
                    </span>
                    <span className="text-sky-700 font-medium cursor-pointer hover:underline">
                      Click any citation badge [1] to inspect exact source passage &rarr;
                    </span>
                  </div>
                )}
              </div>
            )}
          </section>

          {/* Right Citation Drawer / Source Verification Panel (5 cols) */}
          <section className="lg:col-span-5 flex flex-col space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex-1 flex flex-col">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-sky-700" />
                  <h3 className="text-sm font-bold text-slate-800">Source Passages & Citations</h3>
                </div>
                {response?.citations && (
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    {response.citations.length} Sources
                  </span>
                )}
              </div>

              {/* Citations List */}
              <div className="mt-4 flex-1 overflow-y-auto space-y-4 max-h-[620px] pr-1">
                {response && response.citations.length > 0 ? (
                  response.citations.map((cit) => {
                    const isSelected = activeCitationId === cit.id;
                    return (
                      <div
                        key={cit.id}
                        onClick={() => setActiveCitationId(cit.id)}
                        className={`rounded-lg p-4 border transition cursor-pointer text-xs ${
                          isSelected
                            ? 'bg-sky-50/70 border-sky-400 ring-2 ring-sky-200 shadow-xs'
                            : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <span className="h-5 w-5 rounded bg-sky-700 text-white font-bold flex items-center justify-center text-xs">
                              {cit.id}
                            </span>
                            <span className="font-semibold text-slate-800 truncate max-w-[170px]" title={cit.section}>
                              {cit.section}
                            </span>
                          </div>
                          <span className="bg-white text-slate-600 border border-slate-200 px-2 py-0.5 rounded text-[11px] font-medium">
                            Page {cit.page}
                          </span>
                        </div>

                        <div className="text-slate-700 bg-white p-2.5 rounded border border-slate-200/80 font-mono text-[11px] leading-relaxed mb-2 whitespace-pre-wrap">
                          {cit.passage_text}
                        </div>

                        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                          <span className="truncate max-w-[150px]" title={cit.source}>
                            {cit.source}
                          </span>
                          <span className="font-medium text-sky-700">
                            Relevance: {Math.round(cit.score * 100)}%
                          </span>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="h-64 flex flex-col items-center justify-center text-center p-6 text-slate-400">
                    <HelpCircle className="h-10 w-10 text-slate-300 mb-2 stroke-[1.5]" />
                    <p className="text-sm font-medium text-slate-600">No Citations Yet</p>
                    <p className="text-xs text-slate-400 mt-1 max-w-[220px]">
                      Ask a question on the left to inspect exact source passages and page numbers.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </section>

        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-500">
          DocAnswer RAG Architecture &bull; Offline Indexing &bull; Claude &bull; Hybrid BM25/Cosine &bull; Vercel Serverless
        </div>
      </footer>
    </div>
  );
}
