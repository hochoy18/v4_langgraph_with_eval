/**
 * 占位 — Phase 2+ 接入 LangGraph 研究流。
 */
export default function ResearchPage() {
  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-2xl font-semibold mb-4">Research</h1>
      <p className="text-gray-600 mb-6">
        提交研究查询，查看实时事件流 — Phase 2 接入。
      </p>
      <div className="bg-white p-6 rounded-lg shadow">
        <textarea
          rows={3}
          placeholder="Compare transformer vs Mamba architectures..."
          className="w-full p-3 border rounded mb-4"
          disabled
        />
        <button
          className="px-4 py-2 bg-brand-600 text-white rounded opacity-50 cursor-not-allowed"
          disabled
        >
          Run research (Phase 2)
        </button>
      </div>
    </div>
  );
}