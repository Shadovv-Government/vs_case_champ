"""Recompute case evidence and a conditional rollout model from XLSX and JSON."""

import json
import math
from collections import Counter
from pathlib import Path
from statistics import NormalDist, median

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
MATERIALS = ROOT / "technical" / "archive" / "presentation-data"
OPENS = "Открытия карточки товара из контента"
ORDERS = "Заказы через чекаут"


def case_evidence():
    workbook = load_workbook(ROOT / "sources" / "dataset.xlsx", read_only=True, data_only=True)
    try:
        businesses = iter(workbook["Бизнесы"].values)
        columns = next(businesses)
        goods = [
            dict(zip(columns, row))
            for row in businesses
            if row[2] in ("товарное", "товарное и услужное")
        ]
        checkout = [row for row in goods if row["Подключён чекаут"] == 1]
        ready = [row for row in checkout if row["Число активных товаров в каталоге"] > 0]
        with_orders = sum(row[ORDERS] > 0 for row in goods)
        zero_orders = [row for row in ready if row[ORDERS] == 0]
        warm = [row for row in zero_orders if row[OPENS] > 0]
        strict = [row for row in warm if row[OPENS] >= 10]
        ready_with_opens = [row for row in ready if row[OPENS] > 0]
        warm_openings = sum(row[OPENS] for row in warm)
        open_groups = [
            ("0", [row for row in ready if row[OPENS] == 0]),
            ("1–9", [row for row in ready if 1 <= row[OPENS] < 10]),
            ("≥10", [row for row in ready if row[OPENS] >= 10]),
        ]
        cohort_stats = []
        for label, rows in open_groups:
            sold = sum(row[ORDERS] > 0 for row in rows)
            cohort_stats.append({
                "openings": label, "communities": len(rows), "selling": sold,
                "selling_rate": sold / len(rows) if rows else 0,
            })
        sources = {
            name.strip(): count
            for name, count, *_ in list(workbook["Маркет Вконтакте — источники"].values)[1:]
            if isinstance(count, (int, float))
        }
        total = sum(sources.values())
        market_totals = {row[0]: row[1:3] for row in workbook["Маркет Вконтакте — итоги"].values}
        market_orders, partner_orders = market_totals["Оформленные заказы"]
        return {
            "source": "sources/dataset.xlsx",
            "synthetic": True,
            "goods_communities": len(goods),
            "checkout_enabled": len(checkout),
            "selling_in_month": with_orders,
            "checkout_and_catalog": len(ready),
            "ready_with_content_opens": len(ready_with_opens),
            "ready_with_content_opens_and_orders": sum(
                row[ORDERS] > 0 for row in ready_with_opens
            ),
            "ready_orders_without_content_opens": cohort_stats[0]["selling"],
            "ready_zero_orders": len(zero_orders),
            "ready_zero_orders_zero_content_opens": len(zero_orders) - len(warm),
            "warm_zero_orders": len(warm),
            "warm_at_least_10_opens": len(strict),
            "warm_median_opens": median(row[OPENS] for row in warm),
            "strict_median_opens": median(row[OPENS] for row in strict),
            "strict_opening_share": sum(row[OPENS] for row in strict) / warm_openings,
            "strict_topics": dict(Counter(row["Тематика"] for row in strict).most_common()),
            "cohort_stats": cohort_stats,
            "thresholds": [
                {
                    "openings_at_least": threshold,
                    "communities_without_orders": sum(row[OPENS] >= threshold for row in warm),
                    "opening_share": sum(row[OPENS] for row in warm if row[OPENS] >= threshold)
                    / warm_openings,
                }
                for threshold in (1, 5, 10, 25)
            ],
            "checkout_pct": 100 * len(checkout) / len(goods),
            "selling_pct": 100 * with_orders / len(goods),
            "market_total_opens": total,
            "market_orders": market_orders,
            "market_paid_orders": market_totals["Оплаченные заказы"][0],
            "partner_orders": partner_orders,
            "partner_direct_clicks": market_totals["Прямые переходы к Партнёру 1 (без открытия карточки)"][1],
            "traffic": {
                name: {"opens": count, "share_pct": 100 * count / total}
                for name, count in sources.items()
            },
        }
    finally:
        workbook.close()


def project(inputs, evidence):
    economics = inputs["economics"]
    ramp = inputs["ramp"]
    if len(ramp) != 12 or any(not 0 <= fraction <= 1 for fraction in ramp):
        raise ValueError("Expected 12 rollout fractions between 0 and 1")
    target_share = evidence["warm_zero_orders"] / evidence["goods_communities"]
    strict_share = evidence["warm_at_least_10_opens"] / evidence["goods_communities"]
    targets = inputs["reference_goods_communities"] * target_share
    strict_targets = inputs["reference_goods_communities"] * strict_share
    invited_reference = inputs["reference_invited_communities"]
    aov = economics["aov_rub"]
    fee = aov * economics["service_fee"]
    contribution = (
        fee - aov * economics["acquiring"] - economics["variable_cost_per_paid_order_rub"]
    )
    seller_contribution = aov * economics["seller_gross_margin"] - economics["seller_fulfillment_rub"]
    fixed = economics["monthly_fixed_rub"]
    development = economics["development_rub"]
    monthly_hurdle = fixed + development / economics["steady_payback_months"]
    results = {}
    for name, scenario in inputs["scenarios"].items():
        rates = (
            "reach", "adoption", "seller_rate_lift", "paid_share",
            "fulfillment_share", "incremental_sales_share",
        )
        if any(not 0 <= scenario[rate] <= 1 for rate in rates):
            raise ValueError(f"Invalid fraction in scenario {name}")
        if scenario["paid_share"] > scenario["fulfillment_share"]:
            raise ValueError(f"Paid and fulfilled orders exceed all fulfilled orders in {name}")
        order_lift = scenario["orders_per_adopter"]
        if order_lift < scenario["seller_rate_lift"]:
            raise ValueError(f"Order lift is smaller than the selling-business lift in {name}")
        reached = targets * scenario["reach"]
        adopters = reached * scenario["adoption"]
        orders = adopters * order_lift
        selling = adopters * scenario["seller_rate_lift"]
        net_sales_share = scenario["fulfillment_share"] * scenario["incremental_sales_share"]
        unit_contribution = contribution * scenario["paid_share"]
        threshold = math.ceil(monthly_hurdle / unit_contribution) if unit_contribution > 0 else None
        months = [
            {
                "month": month,
                "scale": scale,
                "incremental_orders": orders * scale,
                "incremental_selling_communities": selling * scale,
                "incremental_merchant_sales": orders * scale * net_sales_share,
                "vk_fee_revenue_rub": orders * scale * scenario["paid_share"] * fee,
                "vk_cash_flow_rub": orders * scale * unit_contribution - fixed
                - (development if month == 1 else 0),
            }
            for month, scale in enumerate(ramp, 1)
        ]
        year_cash_flow = sum(month["vk_cash_flow_rub"] for month in months)
        adopter_months = adopters * sum(ramp)
        results[name] = {
            **scenario,
            "reached": reached,
            "adopters": adopters,
            "monthly_incremental_orders_at_scale": orders,
            "monthly_incremental_selling_communities_at_scale": selling,
            "monthly_incremental_orders_per_reached_community": orders / reached if reached else 0,
            "monthly_orders_per_reference_invites": invited_reference * scenario["adoption"] * order_lift,
            "monthly_selling_per_reference_invites": invited_reference
            * scenario["adoption"] * scenario["seller_rate_lift"],
            "monthly_net_merchant_sales_per_reference_invites": invited_reference
            * scenario["adoption"] * order_lift * net_sales_share,
            "monthly_orders_strict_pool_at_scale": strict_targets * scenario["reach"]
            * scenario["adoption"] * order_lift,
            "monthly_vk_fee_revenue_rub_at_scale": orders * scenario["paid_share"] * fee,
            "monthly_order_hurdle": threshold,
            "orders_per_adopter_for_payback": threshold / adopters if threshold and adopters else None,
            "year_one_orders": sum(month["incremental_orders"] for month in months),
            "year_one_vk_cash_flow_rub": year_cash_flow,
            "year_one_other_contribution_needed_per_adopter_month_rub":
                max(0, -year_cash_flow) / adopter_months if adopter_months else None,
            "months": months,
        }

    return {
        "reference_goods_communities": inputs["reference_goods_communities"],
        "reference_invited_communities": invited_reference,
        "eligible_share": target_share,
        "eligible_share_strict": strict_share,
        "eligible": targets,
        "economics": economics,
        "vk_contribution_per_paid_order_rub": contribution,
        "seller_contribution_per_completed_order_without_service_rub": seller_contribution,
        "seller_contribution_per_completed_order_with_service_rub": seller_contribution - fee,
        "monthly_fixed_plus_development_rub": monthly_hurdle,
        "scenarios": results,
    }


def pilot_plan(inputs):
    pilot = inputs["pilot"]
    normal = NormalDist()
    critical = normal.inv_cdf(1 - pilot["alpha"] / 2) + normal.inv_cdf(pilot["power"])
    effect = pilot["minimum_orders_per_invited"]
    sample_sizes = [
        {
            "order_variance": variance,
            "per_arm": math.ceil(2 * critical ** 2 * variance / effect ** 2),
            "per_arm_with_reserve": math.ceil(
                2 * critical ** 2 * variance / effect ** 2 / (1 - pilot["planning_reserve"])
            ),
        }
        for variance in pilot["variance_scenarios"]
    ]
    return {
        **pilot,
        "pre_experiment_budget_rub": sum(
            pilot[key] for key in ("research_rub", "prototype_rub", "instrumentation_and_qa_rub")
        ),
        "sample_sizes": sample_sizes,
    }


def main():
    evidence = case_evidence()
    inputs = json.loads((MATERIALS / "scenario_inputs.json").read_text(encoding="utf-8"))
    evidence["projection"] = project(inputs, evidence)
    evidence["pilot"] = pilot_plan(inputs)
    (MATERIALS / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
