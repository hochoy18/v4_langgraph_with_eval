/**
 * 占位 — Phase 1 接入真实登录。
 */
export default function LoginPage() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow">
        <h1 className="text-2xl font-semibold mb-2">Deep Research</h1>
        <p className="text-sm text-gray-500 mb-6">
          Login 页面 — Phase 1 接入
        </p>
        <input
          type="email"
          placeholder="alice@acme.test"
          className="w-full mb-3 px-3 py-2 border rounded"
          disabled
        />
        <input
          type="password"
          placeholder="••••••"
          className="w-full mb-4 px-3 py-2 border rounded"
          disabled
        />
        <button
          className="w-full py-2 bg-brand-600 text-white rounded opacity-50 cursor-not-allowed"
          disabled
        >
          Sign in (Phase 1)
        </button>
      </div>
    </div>
  );
}