"""
Módulo de analítica electoral para ejecución del plan de 15 días.

Incluye:
- Definición y cálculo de métricas de acierto.
- Baseline de encuesta más reciente.
- Backtesting histórico contra resultados oficiales.
- Unificación de bases heterogéneas (encuestas + posts + catálogo de perfiles).
- Ponderación poblacional de volumen digital por territorio.
- Comparación de modelos (encuesta, social, híbrido) con validación out-of-time.
- Generación de insights operativos para dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class AccuracyMetrics:
    """Métricas clave del sistema de acierto."""

    mae: float
    rmse: float
    ranking_accuracy: float
    calibration_error: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "mae": self.mae,
            "rmse": self.rmse,
            "ranking_accuracy": self.ranking_accuracy,
            "calibration_error": self.calibration_error,
        }


def _to_share(series: pd.Series) -> pd.Series:
    """Normaliza a proporción [0, 1]. Si detecta escala 0-100, la convierte."""
    numeric = pd.to_numeric(series, errors="coerce")
    max_value = numeric.max(skipna=True)
    if pd.notna(max_value) and max_value > 1.0:
        return numeric / 100.0
    return numeric


def compute_accuracy_metrics(actual: pd.Series, predicted: pd.Series) -> AccuracyMetrics:
    """Calcula métricas estándar de acierto para perfiles comparables."""
    df = pd.DataFrame({"actual": _to_share(actual), "pred": _to_share(predicted)}).dropna()
    if df.empty:
        return AccuracyMetrics(mae=float("nan"), rmse=float("nan"), ranking_accuracy=0.0, calibration_error=float("nan"))

    err = (df["pred"] - df["actual"]).astype(float)
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(np.square(err))))
    calibration_error = float(np.abs(df["pred"].mean() - df["actual"].mean()))

    rank_actual = df["actual"].rank(ascending=False, method="min")
    rank_pred = df["pred"].rank(ascending=False, method="min")
    ranking_accuracy = float((rank_actual == rank_pred).mean())

    return AccuracyMetrics(mae=mae, rmse=rmse, ranking_accuracy=ranking_accuracy, calibration_error=calibration_error)


def latest_poll_baseline(
    polls_df: pd.DataFrame,
    *,
    profile_col: str = "candidato",
    value_col: str = "intencion_voto",
    date_col: str = "fecha",
) -> pd.Series:
    """Baseline: promedio por perfil de la fecha más reciente de encuesta."""
    working = polls_df.copy()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    working[value_col] = _to_share(working[value_col])

    valid = working.dropna(subset=[date_col, profile_col, value_col])
    if valid.empty:
        return pd.Series(dtype=float)

    latest_date = valid[date_col].max()
    latest = valid[valid[date_col] == latest_date]
    baseline = latest.groupby(profile_col)[value_col].mean().sort_values(ascending=False)
    baseline.name = "baseline_latest_poll"
    return baseline


def standardize_historical_schema(
    df: pd.DataFrame,
    *,
    role_value: str,
    role_col: str = "cargo",
    territory_col: str = "territorio",
    default_territory: str = "nayarit",
) -> pd.DataFrame:
    """
    Estandariza columnas mínimas para históricos.

    Mantiene trazabilidad para no mezclar cargos de forma permanente.
    """
    working = df.copy()
    if role_col not in working.columns:
        working[role_col] = role_value
    else:
        working[role_col] = working[role_col].fillna(role_value)

    if territory_col not in working.columns:
        working[territory_col] = default_territory
    else:
        working[territory_col] = working[territory_col].fillna(default_territory)

    return working


def backtest_polls_vs_results(
    polls_df: pd.DataFrame,
    results_df: pd.DataFrame,
    *,
    election_col: str = "election_id",
    profile_col: str = "perfil",
    poll_value_col: str = "poll_share",
    result_value_col: str = "actual_share",
    poll_date_col: str = "poll_date",
) -> Dict[str, object]:
    """
    Ejecuta backtesting histórico:
    - baseline de encuesta más reciente por elección/perfil
    - comparación contra resultados oficiales
    """
    polls = polls_df.copy()
    results = results_df.copy()

    polls[poll_date_col] = pd.to_datetime(polls[poll_date_col], errors="coerce")
    polls[poll_value_col] = _to_share(polls[poll_value_col])
    results[result_value_col] = _to_share(results[result_value_col])

    required_polls = {election_col, profile_col, poll_value_col, poll_date_col}
    required_results = {election_col, profile_col, result_value_col}
    missing_polls = required_polls.difference(polls.columns)
    missing_results = required_results.difference(results.columns)
    if missing_polls:
        raise ValueError(f"Columnas faltantes en polls_df: {sorted(missing_polls)}")
    if missing_results:
        raise ValueError(f"Columnas faltantes en results_df: {sorted(missing_results)}")

    latest_idx = polls.groupby([election_col, profile_col])[poll_date_col].idxmax()
    latest_polls = polls.loc[latest_idx, [election_col, profile_col, poll_value_col]].rename(
        columns={poll_value_col: "predicted_share"}
    )
    joined = latest_polls.merge(
        results[[election_col, profile_col, result_value_col]].rename(columns={result_value_col: "actual_share"}),
        on=[election_col, profile_col],
        how="inner",
    )

    metrics = compute_accuracy_metrics(joined["actual_share"], joined["predicted_share"])
    return {
        "records_compared": int(len(joined)),
        "metrics": metrics.to_dict(),
        "comparison": joined.sort_values([election_col, "predicted_share"], ascending=[True, False]).reset_index(drop=True),
    }


def unify_current_datasets(
    polls_df: pd.DataFrame,
    posts_df: pd.DataFrame,
    profiles_df: Optional[pd.DataFrame] = None,
    *,
    profile_col: str = "perfil",
    role_col: str = "cargo",
    territory_col: str = "territorio",
    poll_date_col: str = "fecha_encuesta",
    post_date_col: str = "fecha_post",
) -> pd.DataFrame:
    """
    Integra encuestas y posts en una capa analítica unificada.

    Conserva variable `cargo` para separar gobernador/municipal en modelado final.
    """
    polls = polls_df.copy()
    posts = posts_df.copy()

    if profile_col not in polls.columns:
        raise ValueError(f"polls_df debe incluir columna '{profile_col}'")
    if profile_col not in posts.columns:
        raise ValueError(f"posts_df debe incluir columna '{profile_col}'")

    if poll_date_col in polls.columns:
        polls[poll_date_col] = pd.to_datetime(polls[poll_date_col], errors="coerce")
    if post_date_col in posts.columns:
        posts[post_date_col] = pd.to_datetime(posts[post_date_col], errors="coerce")

    if role_col not in polls.columns:
        polls[role_col] = "desconocido"
    if role_col not in posts.columns:
        posts[role_col] = "desconocido"
    if territory_col not in polls.columns:
        polls[territory_col] = "nayarit"
    if territory_col not in posts.columns:
        posts[territory_col] = "nayarit"

    # Agregación social por perfil, cargo y territorio
    social_agg = (
        posts.groupby([profile_col, role_col, territory_col], as_index=False)
        .agg(
            post_count=("post_id", "count") if "post_id" in posts.columns else (profile_col, "count"),
            sentiment_mean=("sentiment", "mean") if "sentiment" in posts.columns else (profile_col, lambda s: 0.0),
        )
        .rename(columns={"sentiment_mean": "social_sentiment"})
    )

    # Agregación de encuesta por perfil, cargo y territorio
    if "intencion_voto" in polls.columns:
        polls["intencion_voto"] = _to_share(polls["intencion_voto"])
    poll_agg = polls.groupby([profile_col, role_col, territory_col], as_index=False).agg(
        poll_share=("intencion_voto", "mean") if "intencion_voto" in polls.columns else (profile_col, "count")
    )

    unified = poll_agg.merge(
        social_agg,
        on=[profile_col, role_col, territory_col],
        how="outer",
    )

    if profiles_df is not None and not profiles_df.empty:
        profiles = profiles_df.copy()
        unified = profiles.merge(unified, on=[profile_col], how="left")
        if role_col in profiles.columns:
            unified[role_col] = unified[role_col].fillna(unified[f"{role_col}_x"] if f"{role_col}_x" in unified.columns else profiles[role_col])

    unified["post_count"] = unified["post_count"].fillna(0).astype(int)
    unified["social_sentiment"] = unified["social_sentiment"].fillna(0.0).astype(float)
    unified["poll_share"] = _to_share(unified["poll_share"]).fillna(0.0)

    return unified


def allocate_population_weighted_targets(
    demographics_df: pd.DataFrame,
    *,
    total_posts_target: int,
    territory_col: str = "municipio",
    population_col: str = "poblacion",
    min_posts_per_territory: int = 0,
) -> pd.DataFrame:
    """Distribuye objetivo de scraping de posts en proporción a población."""
    demo = demographics_df[[territory_col, population_col]].copy()
    demo[population_col] = pd.to_numeric(demo[population_col], errors="coerce").fillna(0)
    demo = demo[demo[population_col] > 0]
    if demo.empty:
        raise ValueError("No hay demografía válida para calcular ponderación poblacional.")

    demo["population_weight"] = demo[population_col] / demo[population_col].sum()
    demo["target_posts"] = np.floor(demo["population_weight"] * total_posts_target).astype(int)
    demo["target_posts"] = np.maximum(demo["target_posts"], int(min_posts_per_territory))

    current_total = int(demo["target_posts"].sum())
    gap = int(total_posts_target - current_total)
    if gap != 0:
        order = demo.sort_values("population_weight", ascending=False).index.tolist()
        step = 1 if gap > 0 else -1
        i = 0
        while gap != 0 and order:
            idx = order[i % len(order)]
            next_value = int(demo.at[idx, "target_posts"] + step)
            if next_value >= min_posts_per_territory:
                demo.at[idx, "target_posts"] = next_value
                gap -= step
            i += 1

    return demo.sort_values("target_posts", ascending=False).reset_index(drop=True)


def detect_low_coverage_segments(
    posts_df: pd.DataFrame,
    target_df: pd.DataFrame,
    *,
    territory_col: str = "territorio",
    target_territory_col: str = "municipio",
    target_posts_col: str = "target_posts",
) -> pd.DataFrame:
    """Identifica territorios con déficit de posts para raspado subsecuente."""
    observed = (
        posts_df.groupby(territory_col, as_index=False)
        .size()
        .rename(columns={"size": "observed_posts", territory_col: target_territory_col})
    )
    joined = target_df[[target_territory_col, target_posts_col]].merge(observed, on=target_territory_col, how="left")
    joined["observed_posts"] = joined["observed_posts"].fillna(0).astype(int)
    joined["deficit_posts"] = (joined[target_posts_col] - joined["observed_posts"]).clip(lower=0)
    joined["coverage_ratio"] = np.where(
        joined[target_posts_col] > 0,
        joined["observed_posts"] / joined[target_posts_col],
        1.0,
    )
    return joined.sort_values(["deficit_posts", target_posts_col], ascending=[False, False]).reset_index(drop=True)


def evaluate_competing_models(
    model_df: pd.DataFrame,
    *,
    actual_col: str = "actual_share",
    poll_col: str = "poll_share",
    sentiment_col: str = "social_sentiment",
    post_count_col: str = "post_count",
    time_col: str = "snapshot_date",
    validation_fraction: float = 0.2,
) -> Dict[str, object]:
    """
    Compara 3 enfoques (encuesta, social, híbrido) en split out-of-time.
    Devuelve métricas comparables y pesos seleccionados.
    """
    df = model_df.copy()
    required = [actual_col, poll_col, sentiment_col, post_count_col, time_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Columnas faltantes para modelado: {missing}")

    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col, actual_col, poll_col, sentiment_col, post_count_col]).sort_values(time_col).reset_index(drop=True)
    if len(df) < 6:
        raise ValueError("Se requieren al menos 6 registros temporales para evaluación out-of-time.")

    # Señal social (volumen * sentimiento) normalizada a [0, 1]
    social_signal = (pd.to_numeric(df[sentiment_col], errors="coerce").fillna(0.0) + 1.0) / 2.0
    social_signal = social_signal * np.log1p(pd.to_numeric(df[post_count_col], errors="coerce").clip(lower=0))
    social_min, social_max = float(social_signal.min()), float(social_signal.max())
    if social_max > social_min:
        social_norm = (social_signal - social_min) / (social_max - social_min)
    else:
        social_norm = pd.Series(np.zeros(len(df)), index=df.index, dtype=float)
    df["_social_norm"] = social_norm

    split_idx = max(1, int(round(len(df) * (1 - validation_fraction))))
    train = df.iloc[:split_idx].copy()
    test = df.iloc[split_idx:].copy()

    train_actual = _to_share(train[actual_col])
    test_actual = _to_share(test[actual_col])
    train_poll = _to_share(train[poll_col])
    test_poll = _to_share(test[poll_col])
    train_social = _to_share(train["_social_norm"])
    test_social = _to_share(test["_social_norm"])

    models_test_predictions = {
        "survey_only": test_poll,
        "social_only": test_social,
    }

    # Híbrido: ajustar alpha en train y evaluar en test
    best_alpha = 0.0
    best_train_mae = float("inf")
    for alpha in np.arange(0.0, 1.01, 0.05):
        pred = alpha * train_poll + (1 - alpha) * train_social
        mae = float(np.mean(np.abs(_to_share(pred) - train_actual)))
        if mae < best_train_mae:
            best_train_mae = mae
            best_alpha = float(alpha)
    models_test_predictions["hybrid"] = best_alpha * test_poll + (1 - best_alpha) * test_social

    summary_rows: List[Dict[str, float]] = []
    for model_name, preds in models_test_predictions.items():
        metrics = compute_accuracy_metrics(test_actual, preds)
        summary_rows.append({"model": model_name, **metrics.to_dict()})

    summary = pd.DataFrame(summary_rows).sort_values(["mae", "rmse"], ascending=[True, True]).reset_index(drop=True)
    winner = summary.iloc[0]["model"] if not summary.empty else None

    return {
        "train_size": int(len(train)),
        "test_size": int(len(test)),
        "hybrid_alpha_selected": best_alpha,
        "leader_model": winner,
        "model_metrics": summary,
    }


def build_dashboard_insights(
    predictions_df: pd.DataFrame,
    *,
    profile_col: str = "perfil",
    territory_col: str = "territorio",
    date_col: str = "snapshot_date",
    value_col: str = "predicted_share",
    uncertainty_col: str = "uncertainty",
    alert_threshold: float = 0.03,
) -> Dict[str, object]:
    """
    Genera payload de insights:
    - ranking por territorio
    - tendencia temporal
    - incertidumbre
    - alertas de cambio relevante
    """
    df = predictions_df.copy()
    for col in [profile_col, territory_col, date_col, value_col]:
        if col not in df.columns:
            raise ValueError(f"predictions_df debe incluir columna '{col}'")

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[value_col] = _to_share(df[value_col])
    if uncertainty_col not in df.columns:
        df[uncertainty_col] = 0.0
    df[uncertainty_col] = pd.to_numeric(df[uncertainty_col], errors="coerce").fillna(0.0)

    latest_date = df[date_col].max()
    prev_dates = sorted(d for d in df[date_col].dropna().unique() if d < latest_date)
    prev_date = prev_dates[-1] if prev_dates else None

    latest = df[df[date_col] == latest_date].copy()
    prev = df[df[date_col] == prev_date].copy() if prev_date is not None else pd.DataFrame(columns=df.columns)

    ranking = (
        latest.sort_values([territory_col, value_col], ascending=[True, False])
        .groupby(territory_col)
        .apply(lambda part: part[[profile_col, value_col, uncertainty_col]].to_dict("records"))
        .to_dict()
    )

    trend = latest[[territory_col, profile_col, value_col]].merge(
        prev[[territory_col, profile_col, value_col]].rename(columns={value_col: "previous_value"}),
        on=[territory_col, profile_col],
        how="left",
    )
    trend["delta"] = trend[value_col] - trend["previous_value"].fillna(trend[value_col])

    alerts_df = trend[np.abs(trend["delta"]) >= alert_threshold].copy()
    alerts_df = alerts_df.sort_values("delta", ascending=False)
    alerts = [
        {
            "territorio": row[territory_col],
            "perfil": row[profile_col],
            "delta": float(row["delta"]),
            "new_value": float(row[value_col]),
        }
        for _, row in alerts_df.iterrows()
    ]

    uncertainty = (
        latest.groupby(territory_col, as_index=False)[uncertainty_col]
        .mean()
        .rename(columns={uncertainty_col: "territory_uncertainty"})
        .sort_values("territory_uncertainty", ascending=False)
    )

    return {
        "latest_snapshot": str(latest_date.date()) if pd.notna(latest_date) else None,
        "ranking_by_territory": ranking,
        "trend_table": trend.sort_values([territory_col, "delta"], ascending=[True, False]).reset_index(drop=True),
        "territory_uncertainty": uncertainty.reset_index(drop=True),
        "alerts": alerts,
    }
