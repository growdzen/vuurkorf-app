"use client";

import { useEffect, useState } from "react";
import { listOrders, type AdminOrder } from "@/lib/api";

const MATERIAL_LABELS: Record<string, string> = {
  cortenstaal: "Cortenstaal",
  rvs: "RVS",
  zwart_staal: "Zwart Staal",
};

const STATUS_STYLES: Record<string, string> = {
  confirmed: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  cancelled: "bg-red-100 text-red-800",
};

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString("nl-NL", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function formatPrice(price: number | null): string {
  if (price == null) return "—";
  return new Intl.NumberFormat("nl-NL", {
    style: "currency",
    currency: "EUR",
  }).format(price);
}

export default function AdminPage() {
  const [orders, setOrders] = useState<AdminOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  async function fetchOrders() {
    setLoading(true);
    setError(null);
    try {
      const data = await listOrders();
      // Sort newest first
      data.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setOrders(data);
      setLastRefresh(new Date());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Onbekende fout");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchOrders();
  }, []);

  const totalRevenue = orders.reduce((sum, o) => sum + (o.price ?? 0), 0);
  const confirmedCount = orders.filter((o) => o.status === "confirmed").length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gray-900 text-white px-6 py-5 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">
            Vuurkorf — Bestellingen
          </h1>
          <p className="text-gray-400 text-sm mt-0.5">Admin dashboard</p>
        </div>
        <button
          onClick={fetchOrders}
          disabled={loading}
          className="bg-orange-600 hover:bg-orange-500 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          {loading ? "Laden…" : "Vernieuwen"}
        </button>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500 mb-1">Totaal bestellingen</p>
            <p className="text-3xl font-bold text-gray-900">{orders.length}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500 mb-1">Bevestigd</p>
            <p className="text-3xl font-bold text-green-600">{confirmedCount}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500 mb-1">Totale omzet</p>
            <p className="text-3xl font-bold text-orange-600">
              {formatPrice(totalRevenue)}
            </p>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-red-700 text-sm">
            <strong>Fout bij laden:</strong> {error}
          </div>
        )}

        {/* Table */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Alle bestellingen</h2>
            <span className="text-xs text-gray-400">
              Bijgewerkt om {lastRefresh.toLocaleTimeString("nl-NL")}
            </span>
          </div>

          {loading && orders.length === 0 ? (
            <div className="py-16 text-center text-gray-400 text-sm">
              Bestellingen laden…
            </div>
          ) : orders.length === 0 ? (
            <div className="py-16 text-center text-gray-400 text-sm">
              Nog geen bestellingen ontvangen.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
                  <tr>
                    <th className="text-left px-5 py-3 font-medium">Datum</th>
                    <th className="text-left px-5 py-3 font-medium">Klant</th>
                    <th className="text-left px-5 py-3 font-medium">E-mail</th>
                    <th className="text-left px-5 py-3 font-medium">Materiaal</th>
                    <th className="text-left px-5 py-3 font-medium">Dikte</th>
                    <th className="text-right px-5 py-3 font-medium">Prijs</th>
                    <th className="text-left px-5 py-3 font-medium">Status</th>
                    <th className="text-left px-5 py-3 font-medium">Order ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {orders.map((order) => (
                    <tr
                      key={order.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-5 py-3 text-gray-600 whitespace-nowrap">
                        {formatDate(order.created_at)}
                      </td>
                      <td className="px-5 py-3 font-medium text-gray-900 whitespace-nowrap">
                        {order.name}
                      </td>
                      <td className="px-5 py-3 text-gray-600">
                        <a
                          href={`mailto:${order.email}`}
                          className="hover:text-orange-600 transition-colors"
                        >
                          {order.email}
                        </a>
                      </td>
                      <td className="px-5 py-3 text-gray-700">
                        {MATERIAL_LABELS[order.material] ?? order.material}
                      </td>
                      <td className="px-5 py-3 text-gray-700">
                        {order.thickness}mm
                      </td>
                      <td className="px-5 py-3 text-right font-semibold text-gray-900 whitespace-nowrap">
                        {formatPrice(order.price)}
                      </td>
                      <td className="px-5 py-3">
                        <span
                          className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            STATUS_STYLES[order.status] ??
                            "bg-gray-100 text-gray-700"
                          }`}
                        >
                          {order.status}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-gray-400 font-mono text-xs">
                        {order.id.split("-")[0]}…
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
