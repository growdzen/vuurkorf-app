"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  uploadImage,
  startProcessing,
  getPreview,
  createOrder,
  type PreviewResponse,
  type ValidationResult,
  type PricingResult,
} from "@/lib/api";

// ─── Types ───────────────────────────────────────────────────────────────────

type Material = "cortenstaal" | "rvs" | "zwart_staal";
type Thickness = 2 | 3 | 4 | 6;

interface WizardState {
  step: 1 | 2 | 3 | 4 | 5;
  material: Material;
  thickness: Thickness;
  file: File | null;
  filePreviewUrl: string | null;
  jobId: string | null;
  jobStatus: string | null;
  jobStep: string | null;
  jobError: string | null;
  svg: string | null;
  validation: ValidationResult | null;
  pricing: PricingResult | null;
  scale: number;
  offsetX: number;
  offsetY: number;
  name: string;
  email: string;
  orderLoading: boolean;
  orderId: string | null;
}

const MATERIAL_LABELS: Record<Material, string> = {
  cortenstaal: "Cortenstaal",
  rvs: "RVS (Roestvrij Staal)",
  zwart_staal: "Zwart Staal",
};

const MATERIAL_DESCRIPTIONS: Record<Material, string> = {
  cortenstaal: "Warm roestig patina. Tijdloos karakter voor buiten.",
  rvs: "Glanzend en weerbestendig. Modern en onderhoudsvriendelijk.",
  zwart_staal: "Mat zwart. Strak design, scherpe prijs.",
};

const STEP_LABELS = [
  "Materiaal",
  "Foto",
  "Verwerking",
  "Preview",
  "Bestelling",
];

const JOB_STEP_LABELS: Record<string, string> = {
  upload: "Bestand geladen...",
  remove_background: "Achtergrond verwijderen (AI)...",
  silhouette: "Silhouet genereren...",
  vectorize: "Vectoriseren...",
  integrate: "Integreren in template...",
  validate: "Maakbaarheid controleren...",
  done: "Klaar!",
};

// ─── Sub-components ───────────────────────────────────────────────────────────

function StepIndicator({ current }: { current: number }) {
  return (
    <div className="flex items-center justify-center gap-2 mb-10">
      {STEP_LABELS.map((label, i) => {
        const n = i + 1;
        const isActive = n === current;
        const isDone = n < current;
        return (
          <div key={n} className="flex items-center gap-2">
            <div className="flex flex-col items-center">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                  isDone
                    ? "bg-green-500 text-white"
                    : isActive
                    ? "bg-orange-600 text-white"
                    : "bg-gray-200 text-gray-500"
                }`}
              >
                {isDone ? "✓" : n}
              </div>
              <span
                className={`text-xs mt-1 hidden md:block ${
                  isActive ? "text-orange-600 font-semibold" : "text-gray-400"
                }`}
              >
                {label}
              </span>
            </div>
            {i < STEP_LABELS.length - 1 && (
              <div
                className={`h-0.5 w-8 md:w-12 mb-4 ${
                  n < current ? "bg-green-400" : "bg-gray-200"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

function FeasibilityBadge({ status }: { status: "green" | "orange" | "red" }) {
  const config = {
    green: {
      label: "Goed maakbaar",
      cls: "bg-green-100 text-green-800 border-green-300",
    },
    orange: {
      label: "Controleer details",
      cls: "bg-yellow-100 text-yellow-800 border-yellow-300",
    },
    red: {
      label: "Aanpassingen nodig",
      cls: "bg-red-100 text-red-800 border-red-300",
    },
  };
  const { label, cls } = config[status];
  return (
    <span className={`inline-block border rounded-full px-3 py-1 text-sm font-semibold ${cls}`}>
      {status === "green" ? "✓" : status === "orange" ? "⚠" : "✗"} {label}
    </span>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function ConfiguratorPage() {
  const router = useRouter();
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const dropRef = useRef<HTMLDivElement>(null);

  const [state, setState] = useState<WizardState>({
    step: 1,
    material: "cortenstaal",
    thickness: 3,
    file: null,
    filePreviewUrl: null,
    jobId: null,
    jobStatus: null,
    jobStep: null,
    jobError: null,
    svg: null,
    validation: null,
    pricing: null,
    scale: 1.0,
    offsetX: 0,
    offsetY: 0,
    name: "",
    email: "",
    orderLoading: false,
    orderId: null,
  });

  const set = (patch: Partial<WizardState>) =>
    setState((s) => ({ ...s, ...patch }));

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  // ── Step 1: Material & Thickness ──────────────────────────────────────────

  const renderStep1 = () => (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Kies uw materiaal
      </h2>
      <p className="text-gray-500 mb-8">
        Selecteer het materiaal en de dikte van uw vuurkorf.
      </p>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {(Object.keys(MATERIAL_LABELS) as Material[]).map((mat) => (
          <div
            key={mat}
            onClick={() => set({ material: mat })}
            className={`radio-card cursor-pointer ${
              state.material === mat
                ? "radio-card-selected border-orange-500"
                : "radio-card-unselected"
            }`}
          >
            <div className="font-semibold text-gray-900 mb-1">
              {MATERIAL_LABELS[mat]}
            </div>
            <div className="text-sm text-gray-500">
              {MATERIAL_DESCRIPTIONS[mat]}
            </div>
            {state.material === mat && (
              <div className="mt-2 text-orange-600 text-sm font-medium">
                ✓ Geselecteerd
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mb-8">
        <h3 className="font-semibold text-gray-800 mb-3">
          Dikte (mm)
        </h3>
        <div className="flex gap-3">
          {([2, 3, 4, 6] as Thickness[]).map((t) => (
            <button
              key={t}
              onClick={() => set({ thickness: t })}
              className={`w-16 h-16 rounded-xl border-2 font-bold text-lg transition-all ${
                state.thickness === t
                  ? "border-orange-500 bg-orange-50 text-orange-700"
                  : "border-gray-200 text-gray-600 hover:border-gray-300"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Dikte bepaalt sterkte en prijs. 3mm is het populairste formaat.
        </p>
      </div>

      <button
        onClick={() => set({ step: 2 })}
        className="bg-orange-600 hover:bg-orange-500 text-white font-bold py-3 px-8 rounded-xl transition-colors"
      >
        Volgende stap →
      </button>
    </div>
  );

  // ── Step 2: File Upload ───────────────────────────────────────────────────

  const handleFileDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const file = e.dataTransfer.files?.[0];
      if (file) handleFileSelect(file);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const handleFileSelect = (file: File) => {
    const allowed = ["image/jpeg", "image/png", "image/webp"];
    if (!allowed.includes(file.type)) {
      alert("Alleen JPG, PNG of WEBP bestanden toegestaan.");
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      alert("Bestand te groot. Maximum is 20MB.");
      return;
    }
    const url = URL.createObjectURL(file);
    set({ file, filePreviewUrl: url });
  };

  const renderStep2 = () => (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Upload uw foto
      </h2>
      <p className="text-gray-500 mb-8">
        Upload een duidelijke foto. Portretten, dieren, logo&apos;s en
        silhouetten werken het beste.
      </p>

      <div
        ref={dropRef}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleFileDrop}
        onClick={() => document.getElementById("file-input")?.click()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
          state.file
            ? "border-green-400 bg-green-50"
            : "border-gray-300 hover:border-orange-400 hover:bg-orange-50"
        }`}
      >
        <input
          id="file-input"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFileSelect(file);
          }}
        />
        {state.filePreviewUrl ? (
          <div>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={state.filePreviewUrl}
              alt="Preview"
              className="max-h-48 mx-auto rounded-lg mb-3 object-contain"
            />
            <p className="text-green-700 font-semibold">{state.file?.name}</p>
            <p className="text-gray-400 text-sm mt-1">
              Klik om een ander bestand te kiezen
            </p>
          </div>
        ) : (
          <div>
            <div className="text-5xl mb-4">📷</div>
            <p className="text-gray-600 font-semibold mb-1">
              Sleep uw foto hierheen
            </p>
            <p className="text-gray-400 text-sm">
              of klik om te bladeren — JPG, PNG, WEBP — max 20MB
            </p>
          </div>
        )}
      </div>

      <div className="flex gap-4 mt-8">
        <button
          onClick={() => set({ step: 1 })}
          className="border border-gray-300 text-gray-600 font-semibold py-3 px-6 rounded-xl hover:bg-gray-50 transition-colors"
        >
          ← Terug
        </button>
        <button
          disabled={!state.file}
          onClick={() => set({ step: 3 })}
          className="bg-orange-600 hover:bg-orange-500 disabled:bg-gray-300 text-white font-bold py-3 px-8 rounded-xl transition-colors"
        >
          Volgende stap →
        </button>
      </div>
    </div>
  );

  // ── Step 3: Processing ────────────────────────────────────────────────────

  const startPipeline = async () => {
    if (!state.file) return;
    set({ jobStatus: "uploading", jobError: null });

    try {
      // 1. Upload
      const uploadResp = await uploadImage(state.file);
      const jobId = uploadResp.job_id;
      set({ jobId, jobStatus: "pending", jobStep: "upload" });

      // 2. Start processing
      await startProcessing(jobId, state.material, state.thickness);
      set({ jobStatus: "processing" });

      // 3. Poll
      pollRef.current = setInterval(async () => {
        try {
          const preview = await getPreview(jobId);
          set({
            jobStatus: preview.status,
            jobStep: preview.step,
            jobError: preview.error,
          });

          if (preview.status === "completed") {
            if (pollRef.current) clearInterval(pollRef.current);
            set({
              svg: preview.svg ?? null,
              validation: preview.validation ?? null,
              pricing: preview.pricing ?? null,
              step: 4,
            });
          } else if (preview.status === "failed") {
            if (pollRef.current) clearInterval(pollRef.current);
          }
        } catch {
          // keep polling
        }
      }, 2000);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Onbekende fout";
      set({ jobStatus: "failed", jobError: message });
    }
  };

  const renderStep3 = () => {
    const isRunning =
      state.jobStatus === "processing" || state.jobStatus === "pending" || state.jobStatus === "uploading";
    const isFailed = state.jobStatus === "failed";

    return (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          AI verwerking
        </h2>
        <p className="text-gray-500 mb-8">
          Wij verwijderen de achtergrond, maken een silhouet en vectoriseren uw
          afbeelding automatisch.
        </p>

        {!state.jobStatus && (
          <div className="bg-gray-50 rounded-2xl p-8 text-center mb-8">
            <div className="text-5xl mb-4">🤖</div>
            <p className="text-gray-700 font-semibold mb-2">Klaar om te starten</p>
            <p className="text-gray-400 text-sm mb-6">
              Foto:{" "}
              <span className="font-medium text-gray-600">
                {state.file?.name}
              </span>
            </p>
            <button
              onClick={startPipeline}
              className="bg-orange-600 hover:bg-orange-500 text-white font-bold py-3 px-8 rounded-xl transition-colors"
            >
              Start verwerking
            </button>
          </div>
        )}

        {isRunning && (
          <div className="bg-orange-50 border border-orange-200 rounded-2xl p-8 text-center mb-8">
            <div className="text-5xl mb-4 animate-spin">⚙️</div>
            <p className="text-orange-800 font-semibold mb-2">
              {state.jobStep
                ? JOB_STEP_LABELS[state.jobStep] || state.jobStep
                : "Verwerking bezig..."}
            </p>
            <div className="w-full bg-orange-200 rounded-full h-2 mt-4 max-w-xs mx-auto overflow-hidden">
              <div
                className="bg-orange-600 h-2 rounded-full transition-all duration-1000"
                style={{
                  width: (() => {
                    const steps = [
                      "upload",
                      "remove_background",
                      "silhouette",
                      "vectorize",
                      "integrate",
                      "validate",
                      "done",
                    ];
                    const idx = steps.indexOf(state.jobStep || "");
                    return `${Math.max(10, ((idx + 1) / steps.length) * 100)}%`;
                  })(),
                }}
              />
            </div>
            <p className="text-orange-600 text-xs mt-3">
              Dit kan 30-60 seconden duren...
            </p>
          </div>
        )}

        {isFailed && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center mb-8">
            <div className="text-4xl mb-3">❌</div>
            <p className="text-red-800 font-semibold mb-2">
              Verwerking mislukt
            </p>
            <p className="text-red-600 text-sm mb-4">{state.jobError}</p>
            <button
              onClick={() =>
                set({
                  jobStatus: null,
                  jobStep: null,
                  jobError: null,
                  jobId: null,
                })
              }
              className="bg-red-600 hover:bg-red-500 text-white font-bold py-2 px-6 rounded-xl transition-colors"
            >
              Opnieuw proberen
            </button>
          </div>
        )}

        <div className="flex gap-4">
          <button
            onClick={() => {
              if (pollRef.current) clearInterval(pollRef.current);
              set({ step: 2, jobStatus: null, jobStep: null, jobError: null });
            }}
            className="border border-gray-300 text-gray-600 font-semibold py-3 px-6 rounded-xl hover:bg-gray-50 transition-colors"
          >
            ← Terug
          </button>
        </div>
      </div>
    );
  };

  // ── Step 4: Preview ───────────────────────────────────────────────────────

  const renderStep4 = () => (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Uw ontwerp preview
      </h2>
      <p className="text-gray-500 mb-6">
        Pas de schaal en positie aan. Uw motief wordt zichtbaar in de vuurkorf.
      </p>

      <div className="grid md:grid-cols-2 gap-8">
        {/* SVG Preview */}
        <div>
          <div className="bg-gray-100 rounded-2xl p-4 aspect-[4/3] flex items-center justify-center overflow-hidden relative">
            {state.svg ? (
              <div
                className="w-full h-full flex items-center justify-center"
                dangerouslySetInnerHTML={{ __html: state.svg }}
                style={{ maxWidth: "100%", maxHeight: "100%" }}
              />
            ) : (
              <p className="text-gray-400">SVG niet beschikbaar</p>
            )}
          </div>
          <p className="text-xs text-gray-400 text-center mt-2">
            Voorbeeldweergave — niet op schaal
          </p>
        </div>

        {/* Controls */}
        <div className="space-y-6">
          {/* Feasibility */}
          {state.validation && (
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">
                Maakbaarheidsscore
              </h3>
              <FeasibilityBadge status={state.validation.status} />
              {state.validation.issues.length > 0 && (
                <ul className="mt-3 space-y-1">
                  {state.validation.issues.map((issue, i) => (
                    <li key={i} className="text-sm text-yellow-700 flex gap-2">
                      <span>⚠</span>
                      <span>{issue}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Scale slider */}
          <div>
            <label className="block font-semibold text-gray-800 mb-2">
              Schaal: {state.scale.toFixed(2)}x
            </label>
            <input
              type="range"
              min={0.5}
              max={2.0}
              step={0.05}
              value={state.scale}
              onChange={(e) => set({ scale: Number(e.target.value) })}
              className="w-full accent-orange-600"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>0.5x</span>
              <span>2.0x</span>
            </div>
          </div>

          {/* X offset */}
          <div>
            <label className="block font-semibold text-gray-800 mb-2">
              Positie X: {state.offsetX > 0 ? "+" : ""}{state.offsetX}px
            </label>
            <input
              type="range"
              min={-150}
              max={150}
              step={5}
              value={state.offsetX}
              onChange={(e) => set({ offsetX: Number(e.target.value) })}
              className="w-full accent-orange-600"
            />
          </div>

          {/* Y offset */}
          <div>
            <label className="block font-semibold text-gray-800 mb-2">
              Positie Y: {state.offsetY > 0 ? "+" : ""}{state.offsetY}px
            </label>
            <input
              type="range"
              min={-100}
              max={100}
              step={5}
              value={state.offsetY}
              onChange={(e) => set({ offsetY: Number(e.target.value) })}
              className="w-full accent-orange-600"
            />
          </div>

          {/* Pricing */}
          {state.pricing && (
            <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
              <h3 className="font-semibold text-gray-800 mb-3">Prijsoverzicht</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Materiaal ({MATERIAL_LABELS[state.material]})</span>
                  <span>€{state.pricing.material_price.toFixed(2)}</span>
                </div>
                {state.pricing.complexity_surcharge > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Complexiteitstoeslag</span>
                    <span>€{state.pricing.complexity_surcharge.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">Opstartkosten</span>
                  <span>€{state.pricing.setup_fee.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-bold text-gray-900 border-t border-orange-200 pt-2 mt-2">
                  <span>Totaal (incl. BTW)</span>
                  <span className="text-orange-700 text-lg">
                    €{state.pricing.total.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-4 mt-8">
        <button
          onClick={() => set({ step: 3 })}
          className="border border-gray-300 text-gray-600 font-semibold py-3 px-6 rounded-xl hover:bg-gray-50 transition-colors"
        >
          ← Terug
        </button>
        <button
          onClick={() => set({ step: 5 })}
          className="bg-orange-600 hover:bg-orange-500 text-white font-bold py-3 px-8 rounded-xl transition-colors"
        >
          Naar bestelling →
        </button>
      </div>
    </div>
  );

  // ── Step 5: Order ─────────────────────────────────────────────────────────

  const submitOrder = async () => {
    if (!state.jobId || !state.name || !state.email) return;
    set({ orderLoading: true });
    try {
      const resp = await createOrder({
        job_id: state.jobId,
        name: state.name,
        email: state.email,
        material: state.material,
        thickness: state.thickness,
        scale: state.scale,
        offset_x: state.offsetX,
        offset_y: state.offsetY,
      });
      set({ orderId: resp.order_id, orderLoading: false });
      router.push(`/bevestiging?order_id=${resp.order_id}&name=${encodeURIComponent(state.name)}`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Bestelling mislukt";
      alert(message);
      set({ orderLoading: false });
    }
  };

  const renderStep5 = () => (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Bestelling afronden
      </h2>
      <p className="text-gray-500 mb-8">
        Controleer uw bestelling en vul uw gegevens in.
      </p>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Order summary */}
        <div className="bg-gray-50 rounded-2xl p-6">
          <h3 className="font-semibold text-gray-800 mb-4">Samenvatting</h3>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">Materiaal</dt>
              <dd className="font-medium">{MATERIAL_LABELS[state.material]}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Dikte</dt>
              <dd className="font-medium">{state.thickness}mm</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Schaal</dt>
              <dd className="font-medium">{state.scale.toFixed(2)}x</dd>
            </div>
            {state.pricing && (
              <>
                <div className="flex justify-between border-t pt-2 mt-2">
                  <dt className="text-gray-500">Materiaalprijs</dt>
                  <dd>€{state.pricing.material_price.toFixed(2)}</dd>
                </div>
                {state.pricing.complexity_surcharge > 0 && (
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Complexiteitstoeslag</dt>
                    <dd>€{state.pricing.complexity_surcharge.toFixed(2)}</dd>
                  </div>
                )}
                <div className="flex justify-between">
                  <dt className="text-gray-500">Opstartkosten</dt>
                  <dd>€{state.pricing.setup_fee.toFixed(2)}</dd>
                </div>
                <div className="flex justify-between font-bold text-gray-900 border-t pt-2 mt-2 text-base">
                  <dt>Totaal</dt>
                  <dd className="text-orange-600">
                    €{state.pricing.total.toFixed(2)}
                  </dd>
                </div>
              </>
            )}
          </dl>
        </div>

        {/* Contact form */}
        <div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Naam *
              </label>
              <input
                type="text"
                value={state.name}
                onChange={(e) => set({ name: e.target.value })}
                placeholder="Uw volledige naam"
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                E-mailadres *
              </label>
              <input
                type="email"
                value={state.email}
                onChange={(e) => set({ email: e.target.value })}
                placeholder="uw@email.nl"
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
              />
            </div>
            <p className="text-xs text-gray-400">
              Wij nemen contact met u op voor betaling en levering.
              Uw gegevens worden niet gedeeld met derden.
            </p>
          </div>

          {state.validation && state.validation.status === "red" && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
              ⚠ Uw ontwerp heeft maakbaarheidsproblemen. Wij nemen contact op
              voor aanpassingen voordat er geproduceerd wordt.
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-4 mt-8">
        <button
          onClick={() => set({ step: 4 })}
          className="border border-gray-300 text-gray-600 font-semibold py-3 px-6 rounded-xl hover:bg-gray-50 transition-colors"
        >
          ← Terug
        </button>
        <button
          disabled={!state.name || !state.email || state.orderLoading}
          onClick={submitOrder}
          className="bg-orange-600 hover:bg-orange-500 disabled:bg-gray-300 text-white font-bold py-3 px-8 rounded-xl transition-colors flex items-center gap-2"
        >
          {state.orderLoading ? (
            <>
              <span className="animate-spin">⚙️</span> Bestelling plaatsen...
            </>
          ) : (
            "Bestelling plaatsen ✓"
          )}
        </button>
      </div>
    </div>
  );

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <StepIndicator current={state.step} />

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
        {state.step === 1 && renderStep1()}
        {state.step === 2 && renderStep2()}
        {state.step === 3 && renderStep3()}
        {state.step === 4 && renderStep4()}
        {state.step === 5 && renderStep5()}
      </div>
    </div>
  );
}
