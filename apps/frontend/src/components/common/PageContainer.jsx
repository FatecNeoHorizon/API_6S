export function PageContainer({ children }) {
  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-6xl">{children}</div>
    </div>
  );
}