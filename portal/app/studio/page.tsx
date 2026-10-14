"use client";

import { useState } from "react";
import { Play, Database, FileText } from "lucide-react";

export default function TrainingStudio() {
  const [jobType, setJobType] = useState("sft");
  const [namespace, setNamespace] = useState("default");
  const [samples, setSamples] = useState(10);
  const [status, setStatus] = useState<string | null>(null);

  const startJob = async () => {
    setStatus("started");
    // Mock simulation
    setTimeout(() => {
      setStatus("completed");
    }, 2000);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6 text-white">Training & Dataset Studio</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
          <h2 className="text-xl font-semibold mb-4 text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Job Configuration
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Dataset Type</label>
              <select
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-white"
              >
                <option value="sft">Synthetic SFT (Instruction-Response)</option>
                <option value="raft">RAFT (with Distractors & CoT)</option>
                <option value="mining">Hard Negative Mining</option>
                <option value="dedup">Semantic Deduplication</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Namespace</label>
              <input
                type="text"
                value={namespace}
                onChange={(e) => setNamespace(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-white"
              />
            </div>

            {(jobType === 'sft' || jobType === 'raft') && (
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">Samples to Generate</label>
                <input
                  type="number"
                  value={samples}
                  onChange={(e) => setSamples(parseInt(e.target.value) || 10)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-white"
                />
              </div>
            )}

            <button
              onClick={startJob}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
            >
              <Play className="w-4 h-4" />
              Start Generation Job
            </button>
          </div>
        </div>

        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
          <h2 className="text-xl font-semibold mb-4 text-white">Job Status</h2>

          {status === null ? (
            <div className="h-40 flex items-center justify-center text-slate-500">
              No active jobs.
            </div>
          ) : status === "started" ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-blue-400">
                <div className="animate-spin w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full" />
                <span>Job is running...</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2.5">
                <div className="bg-blue-600 h-2.5 rounded-full w-1/2 animate-pulse"></div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-green-400 font-medium">
                <div className="w-2 h-2 bg-green-400 rounded-full" />
                Job Completed Successfully
              </div>
              <p className="text-slate-400 text-sm">Generated {samples} samples.</p>

              <button className="w-full bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2">
                <FileText className="w-4 h-4" />
                Download JSONL
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
