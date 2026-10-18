"""plotting.py - Figures for the report (saved as PNG, 200 dpi)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon

INK, MUTED = "#1f2933", "#7b8794"
C_CRANE = ["#c0392b", "#1f6fb2"]
C_PICK = ["#2e8b57", "#d4881c"]


def _modules(ax, prob, highlight=None):
    seen = set()
    for r in prob.df.itertuples():
        key = (r.x, r.y)
        if key in seen:
            continue
        seen.add(key)
        fc = "#cbd2d9"
        if highlight is not None:
            fc = highlight.get(key, fc)
        ax.add_patch(Rectangle((r.x - r.width / 2, r.y - r.length / 2), r.width, r.length,
                               fc=fc, ec="#616e7c", lw=0.6))
        if prob.N <= 60:
            ax.text(r.x, r.y, str(r.id), ha="center", va="center", fontsize=6, color=INK)


def layout(prob, x, title, path, K=1, cranes=None, note=None):
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    _modules(ax, prob)
    if prob.site.pickup_outside_hull:
        ax.add_patch(Polygon(prob.hull_pts, fill=False, ls=":", ec=MUTED, lw=1,
                             label="Building outline (no trucks inside)"))
    cranes = cranes or [prob.crane]
    nC = len(cranes)
    for j, cr in enumerate(cranes):
        c = x[2 * j: 2 * j + 2]
        ax.add_patch(Circle(c, cr.radius, fill=False, ls="--", ec=C_CRANE[j], lw=1))
        ax.add_patch(Rectangle(c - cr.base_size / 2, cr.base_size, cr.base_size, fc=C_CRANE[j],
                               label=f"{cr.name} ({cr.radius:.0f} m jib)"))
    pk = np.asarray(x[2 * nC:]).reshape(-1, 2)
    for k, p in enumerate(pk):
        w, l = prob.site.pickup_w, prob.site.pickup_l
        ax.add_patch(Rectangle((p[0] - w / 2, p[1] - l / 2), w, l, fc=C_PICK[k % 2], alpha=0.55,
                               ec=C_PICK[k % 2], label=f"Pickup bay {k+1}"))
    xr, yr = prob.site.x_range, prob.site.y_range
    ax.set_xlim(*xr); ax.set_ylim(*yr); ax.set_aspect("equal")
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    ax.set_title(title, fontsize=10, color=INK, loc="left")
    if note:
        ax.text(0.01, 0.01, note, transform=ax.transAxes, fontsize=7.5, color=INK,
                va="bottom", bbox=dict(fc="white", ec="none", alpha=0.8))
    ax.legend(loc="upper right", fontsize=7, frameon=True)
    ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def convergence(histories, labels, path, ref=None):
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for h, lab, col in zip(histories, labels, ["#7b8794", "#1f6fb2", "#c0392b"]):
        L = max(len(x) for x in h)
        arr = np.array([np.pad(x, (0, L - len(x)), mode="edge") for x in h])
        arr = np.where(np.isfinite(arr), arr, np.nan)
        med = np.nanmedian(arr, 0)
        ax.plot(med, color=col, lw=1.6, label=f"{lab} (median of {len(h)} runs)")
        ax.fill_between(range(L), np.nanpercentile(arr, 10, 0), np.nanpercentile(arr, 90, 0),
                        color=col, alpha=0.15)
    if ref is not None:
        ax.axhline(ref, color=INK, ls=":", lw=1, label=f"Global optimum (grid) {ref:.1f} s")
    ax.set_xlabel("Generation"); ax.set_ylabel("Best total time (s)")
    lo = ref * 0.98 if ref else None
    ax.set_ylim(lo, (ref or 0) * 1.25 if ref else None)
    ax.legend(fontsize=7.5); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def benchmark_box(data, labels, path, ref=None, title=""):
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    ax.boxplot(data, vert=False, tick_labels=labels, widths=0.5,
               medianprops=dict(color="#c0392b"), flierprops=dict(markersize=3))
    for i, d in enumerate(data, 1):
        ax.scatter(d, np.random.default_rng(i).normal(i, 0.05, len(d)), s=8, color="#1f6fb2", alpha=0.6, zorder=3)
    if ref:
        ax.axvline(ref, color=INK, ls=":", lw=1)
        ax.text(ref, len(data) + 0.45, f" global optimum {ref:.0f} s", fontsize=7, color=INK)
    ax.set_xlabel("Best total time found per run (s)"); ax.set_title(title, fontsize=10, loc="left")
    ax.grid(alpha=0.25, axis="x")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def stacked_breakdown(rows, path, title):
    """rows: list of (label, {component: seconds})"""
    keys = list(rows[0][1].keys())
    cols = ["#1f6fb2", "#5aa0d8", "#2e8b57", "#d4881c", "#7b8794", "#c0392b"]
    fig, ax = plt.subplots(figsize=(6.6, 0.55 * len(rows) + 1.4))
    left = np.zeros(len(rows))
    for k, c in zip(keys, cols):
        vals = np.array([r[1][k] for r in rows]) / 3600
        ax.barh([r[0] for r in rows], vals, left=left, color=c, label=k, height=0.55)
        left += vals
    for i, l in enumerate(left):
        ax.text(l, i, f" {l:,.1f} h", va="center", fontsize=7.5)
    ax.set_xlabel("Crane time (hours)"); ax.set_title(title, fontsize=10, loc="left")
    ax.invert_yaxis(); ax.legend(fontsize=7, ncol=3, loc="lower right"); ax.grid(alpha=0.25, axis="x")
    ax.set_xlim(0, left.max() * 1.18)
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def tornado(rows, base, path, title):
    """rows: list of (label, value_low, value_high)"""
    rows = sorted(rows, key=lambda r: abs(r[2] - r[1]))
    fig, ax = plt.subplots(figsize=(6.6, 0.45 * len(rows) + 1.2))
    for i, (lab, lo, hi) in enumerate(rows):
        ax.barh(i, (lo - base) / base * 100, color="#1f6fb2", height=0.55)
        ax.barh(i, (hi - base) / base * 100, color="#c0392b", height=0.55)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_xlabel("Change in optimal crane movement time (%)  [blue: -20%, red: +20% of input]")
    ax.set_title(title, fontsize=10, loc="left"); ax.grid(alpha=0.25, axis="x")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def parity(y, yhat, path, title):
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.scatter(y, yhat, s=6, alpha=0.4, color="#1f6fb2")
    lo, hi = min(y.min(), yhat.min()), max(y.max(), yhat.max())
    ax.plot([lo, hi], [lo, hi], color=INK, lw=0.8, ls=":")
    ax.set_xlabel("Simulated movement time (s)"); ax.set_ylabel("ML-predicted (s)")
    ax.set_title(title, fontsize=10, loc="left"); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)
