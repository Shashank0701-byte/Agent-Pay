const stats = [
  { label: "Agents", value: "12" },
  { label: "Pending approvals", value: "3" },
  { label: "Monthly spend", value: "₹48.5k" },
  { label: "Policy coverage", value: "94%" },
];

const recentActivities = [
  { agent: "Ops Agent", action: "Requested payment", amount: "₹2,450", status: "Pending" },
  { agent: "Analytics Agent", action: "Auto-approved", amount: "₹890", status: "Approved" },
  { agent: "Research Agent", action: "Flagged by policy", amount: "₹8,500", status: "Blocked" },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <header className="mb-10 flex items-center justify-between border-b border-slate-800 pb-6">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-cyan-400">AgentPay</p>
            <h1 className="mt-2 text-3xl font-semibold">Operations dashboard</h1>
          </div>
          <button className="rounded-full bg-cyan-500 px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-400">
            Create agent
          </button>
        </header>

        <section className="grid gap-4 md:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg shadow-slate-950/20">
              <p className="text-sm text-slate-400">{stat.label}</p>
              <p className="mt-3 text-3xl font-semibold text-white">{stat.value}</p>
            </div>
          ))}
        </section>

        <section className="mt-10 grid gap-6 lg:grid-cols-[1.7fr_1fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Recent activity</h2>
              <span className="text-sm text-slate-400">Last 24 hours</span>
            </div>

            <div className="space-y-4">
              {recentActivities.map((item) => (
                <div key={item.agent} className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                  <div>
                    <p className="font-medium text-white">{item.agent}</p>
                    <p className="text-sm text-slate-400">{item.action}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-cyan-300">{item.amount}</p>
                    <p className="text-xs uppercase tracking-wide text-slate-400">{item.status}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">Policy health</h2>
            <div className="mt-6 space-y-5">
              <div>
                <div className="mb-2 flex justify-between text-sm text-slate-300">
                  <span>Allowed categories</span>
                  <span>6/7</span>
                </div>
                <div className="h-2 rounded-full bg-slate-800">
                  <div className="h-2 w-[86%] rounded-full bg-emerald-500" />
                </div>
              </div>
              <div>
                <div className="mb-2 flex justify-between text-sm text-slate-300">
                  <span>Budget adherence</span>
                  <span>72%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-800">
                  <div className="h-2 w-[72%] rounded-full bg-amber-500" />
                </div>
              </div>
              <div>
                <div className="mb-2 flex justify-between text-sm text-slate-300">
                  <span>Approval response</span>
                  <span>96%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-800">
                  <div className="h-2 w-[96%] rounded-full bg-cyan-500" />
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
