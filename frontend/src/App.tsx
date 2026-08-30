import { useEffect, useState } from "react";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking backend...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((response) => response.json())
      .then((data) => {
        setBackendStatus(data.status);
      })
      .catch(() => {
        setBackendStatus("Backend unavailable");
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">
          AI Developer Copilot
        </h1>

        <p className="text-slate-400 mb-6">
          AI-powered development assistant
        </p>

        <div className="rounded-lg bg-slate-900 border border-slate-700 px-6 py-4">
          Backend status:{" "}
          <span className="font-semibold text-green-400">
            {backendStatus}
          </span>
        </div>
      </div>
    </div>
  );
}

export default App;