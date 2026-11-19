"""Recompute case evidence and a conditional rollout model from XLSX and JSON."""

import json
import math
from pathlib import Path
from statistics import median

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
MATERIALS = ROOT / "materials" / "presentation"


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
        with_orders = sum(row["Заказы через чекаут"] > 0 for row in goods)
        openings = [
            row["Открытия карточки товара из контента"]
            for row in ready
            if row["Заказы через чекаут"] == 0
        ]
        warm = sorted(value for value in openings if value > 0)
        ready_with_opens = [
            row for row in ready if row["Открытия карточки товара из контента"] > 0
        ]
        sources = {
            name.strip(): count
            for name, count, *_ in list(workbook["Маркет Вконтакте — источники"].values)[1:]
            if isinstance(count, (int, float))
        }
        total = sum(sources.values())
        return {
            "source": "sources/dataset.xlsx",
            "synthetic": True,
            "goods_communities": len(goods),
            "checkout_enabled": len(checkout),
            "selling_in_month": with_orders,
            "checkout_and_catalog": len(ready),
            "ready_with_content_opens": len(ready_with_opens),
            "ready_with_content_opens_and_orders": sum(
                row["Заказы через чекаут"] > 0 for row in ready_with_opens
            ),
            "ready_zero_orders_zero_content_opens": openings.count(0),
            "warm_zero_orders": len(warm),
            "warm_at_least_10_opens": sum(value >= 10 for value in warm),
            "warm_median_opens": median(warm),
            "checkout_pct": 100 * len(checkout) / len(goods),
            "selling_pct": 100 * with_orders / len(goods),
            "market_total_opens": total,
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
    targets = inputs["reference_goods_communities"] * target_share
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
        rates = ("reach", "adoption", "seller_rate_lift", "paid_share")
        if any(not 0 <= scenario[rate] <= 1 for rate in rates):
            raise ValueError(f"Invalid fraction in scenario {name}")
        order_lift = scenario["orders_per_adopter"]
        if order_lift < scenario["seller_rate_lift"]:
            raise ValueError(f"Order lift is smaller than the selling-business lift in {name}")
        reached = targets * scenario["reach"]
        adopters = reached * scenario["adoption"]
        orders = adopters * order_lift
        selling = adopters * scenario["seller_rate_lift"]
        unit_contribution = contribution * scenario["paid_share"]
        threshold = math.ceil(monthly_hurdle / unit_contribution) if unit_contribution > 0 else None
        months = [
            {
                "month": month,
                "scale": scale,
                "incremental_orders": orders * scale,
                "incremental_selling_communities": selling * scale,
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
        "eligible_share": target_share,
        "eligible_share_strict": evidence["warm_at_least_10_opens"] / evidence["goods_communities"],
        "eligible": targets,
        "economics": economics,
        "vk_contribution_per_paid_order_rub": contribution,
        "seller_contribution_per_completed_order_without_service_rub": seller_contribution,
        "seller_contribution_per_completed_order_with_service_rub": seller_contribution - fee,
        "monthly_fixed_plus_development_rub": monthly_hurdle,
        "scenarios": results,
    }


def main():
    evidence = case_evidence()
    inputs = json.loads((MATERIALS / "scenario_inputs.json").read_text(encoding="utf-8"))
    evidence["projection"] = project(inputs, evidence)
    (MATERIALS / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
