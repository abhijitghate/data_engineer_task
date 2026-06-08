
import pandas as pd
import sys
import logging

LOGGER = logging.getLogger(__name__)


def parse_excel_master(file_path: str) -> dict:
    """
    Parses the MASTER sheet and returns extracted key/value data.

    Args:
        file_path (str): The path to the Excel file.
    Returns:
        dict: Extracted values from the MASTER sheet.
    """
    try:
        LOGGER.info("Reading excel MASTER sheet from %s", file_path)
        df = pd.read_excel(file_path, sheet_name="MASTER", header=None)

        def is_filled(value) -> bool:
            return pd.notna(value) and str(value).strip() != ""

        def find_label_col(row, target_label: str):
            target = target_label.strip().lower()
            for col_index, value in enumerate(row):
                if is_filled(value) and str(value).strip().lower() == target:
                    return col_index
            return None

        raw_data = {}

        for row_index in range(len(df)):
            row = df.iloc[row_index]

            rated_entity_col = find_label_col(row, "Rated entity")
            if rated_entity_col is not None and rated_entity_col + 1 < df.shape[1]:
                raw_data["company_name"] = df.iloc[row_index, rated_entity_col + 1]

            corporate_sector_col = find_label_col(row, "CorporateSector")
            if (
                corporate_sector_col is not None
                and corporate_sector_col + 1 < df.shape[1]
            ):
                raw_data["corporate_sector"] = df.iloc[
                    row_index, corporate_sector_col + 1
                ]

            methodologies_col = find_label_col(row, "Rating methodologies applied")
            if methodologies_col is not None:
                methods = []
                for col_index in range(methodologies_col + 1, df.shape[1]):
                    value = df.iloc[row_index, col_index]
                    if not is_filled(value):
                        break
                    methods.append(str(value).strip())
                raw_data["rating_methodologies_applied"] = methods

            industry_risk_col = find_label_col(row, "Industry risk")
            if industry_risk_col is not None:
                risks = []
                for col_index in range(industry_risk_col + 1, df.shape[1]):
                    risk_name = df.iloc[row_index, col_index]
                    if not is_filled(risk_name):
                        break

                    risk_score = (
                        df.iloc[row_index + 1, col_index]
                        if row_index + 1 < len(df)
                        else None
                    )
                    risk_weight = (
                        df.iloc[row_index + 2, col_index]
                        if row_index + 2 < len(df)
                        else None
                    )

                    risks.append({
                        "industry_risk_name": str(risk_name).strip(),
                        "industry_risk_score": risk_score,
                        "industry_weight": risk_weight,
                    })
                raw_data["industry_risks"] = risks

            segmentation_criteria_col = find_label_col(row, "Segmentation criteria")
            if segmentation_criteria_col is not None:
                raw_data["segmentation_criteria"] = df.iloc[
                    row_index, segmentation_criteria_col + 1
                ]

            reporting_currency_col = find_label_col(row, "Reporting Currency/Units")
            if reporting_currency_col is not None:
                raw_data["reporting_currency"] = df.iloc[
                    row_index, reporting_currency_col + 1
                ]

            country_of_origin_col = find_label_col(row, "Country of origin")
            if country_of_origin_col is not None:
                raw_data["country_of_origin"] = df.iloc[
                    row_index, country_of_origin_col + 1
                ]

            accounting_principles_col = find_label_col(row, "Accounting principles")
            if accounting_principles_col is not None:
                raw_data["accounting_principles"] = df.iloc[
                    row_index, accounting_principles_col + 1
                ]

            end_of_business_month_col = find_label_col(row, "End of business year")
            if end_of_business_month_col is not None:
                raw_data["end_of_business_month"] = df.iloc[
                    row_index, end_of_business_month_col + 1
                ]

            business_risk_profile_col = find_label_col(row, "Business risk profile")
            if business_risk_profile_col is not None:
                raw_data["business_risk_profile"] = df.iloc[
                    row_index, business_risk_profile_col + 1
                ]

            blended_industry_risk_profile_col = find_label_col(
                row, "(Blended) Industry risk profile"
            )
            if blended_industry_risk_profile_col is not None:
                raw_data["blended_industry_risk_profile"] = df.iloc[
                    row_index, blended_industry_risk_profile_col + 1
                ]

            competitive_positioning_col = find_label_col(row, "Competitive Positioning")
            if competitive_positioning_col is not None:
                raw_data["competitive_positioning"] = df.iloc[
                    row_index, competitive_positioning_col + 1
                ]

            market_share_col = find_label_col(row, "Market share")
            if market_share_col is not None:
                raw_data["market_share"] = df.iloc[row_index, market_share_col + 1]

            diversification_col = find_label_col(row, "Diversification")
            if diversification_col is not None:
                raw_data["diversification"] = df.iloc[
                    row_index, diversification_col + 1
                ]

            operating_profitability_col = find_label_col(row, "Operating profitability")
            if operating_profitability_col is not None:
                raw_data["operating_profitability"] = df.iloc[
                    row_index, operating_profitability_col + 1
                ]

            sector_or_company_specific_factor_1_col = find_label_col(
                row, "Sector/company-specific factors (1)"
            )
            if sector_or_company_specific_factor_1_col is not None:
                raw_data["sector_or_company_specific_factor_1"] = df.iloc[
                    row_index, sector_or_company_specific_factor_1_col + 1
                ]

            sector_or_company_specific_factor_2_col = find_label_col(
                row, "Sector/company-specific factors (2)"
            )
            if sector_or_company_specific_factor_2_col is not None:
                raw_data["sector_or_company_specific_factor_2"] = df.iloc[
                    row_index, sector_or_company_specific_factor_2_col + 1
                ]

            financial_risk_profile_col = find_label_col(row, "Financial risk profile")
            if financial_risk_profile_col is not None:
                raw_data["financial_risk_profile"] = df.iloc[
                    row_index, financial_risk_profile_col + 1
                ]

            leverage_col = find_label_col(row, "Leverage")
            if leverage_col is not None:
                raw_data["leverage"] = df.iloc[row_index, leverage_col + 1]

            interest_cover_col = find_label_col(row, "Interest cover")
            if interest_cover_col is not None:
                raw_data["interest_cover"] = df.iloc[row_index, interest_cover_col + 1]

            cash_flow_cover_col = find_label_col(row, "Cash flow cover")
            if cash_flow_cover_col is not None:
                raw_data["cash_flow_cover"] = df.iloc[
                    row_index, cash_flow_cover_col + 1
                ]

            liquidity_assessment_col = find_label_col(row, "Liquidity")
            if liquidity_assessment_col is not None:
                raw_data["liquidity_assessment"] = df.iloc[
                    row_index, liquidity_assessment_col + 1
                ]

            scope_credit_metrics_col = find_label_col(row, "[Scope Credit Metrics]")
            if scope_credit_metrics_col is not None:
                credit_metrics = []
                for col_index in range(scope_credit_metrics_col + 1, df.shape[1]):
                    metric_year = df.iloc[row_index, col_index]
                    if not is_filled(metric_year):
                        break

                    scope_adjusted_ebitda_interest_cover = (
                        df.iloc[row_index + 1, col_index]
                        if row_index + 1 < len(df)
                        else None
                    )
                    scope_adjusted_debt_ebitda = (
                        df.iloc[row_index + 2, col_index]
                        if row_index + 2 < len(df)
                        else None
                    )

                    scope_adjusted_ffo_debt = (
                        df.iloc[row_index + 3, col_index]
                        if row_index + 3 < len(df)
                        else None
                    )
                    scope_adjusted_loan_value = (
                        df.iloc[row_index + 4, col_index]
                        if row_index + 4 < len(df)
                        else None
                    )
                    scope_adjusted_focf_debt = (
                        df.iloc[row_index + 5, col_index]
                        if row_index + 5 < len(df)
                        else None
                    )
                    liquidity = (
                        df.iloc[row_index + 6, col_index]
                        if row_index + 6 < len(df)
                        else None
                    )

                    credit_metrics.append({
                        "metric_year": metric_year,
                        "scope_adjusted_ebitda_interest_cover": scope_adjusted_ebitda_interest_cover,
                        "scope_adjusted_debt_ebitda": scope_adjusted_debt_ebitda,
                        "scope_adjusted_ffo_debt": scope_adjusted_ffo_debt,
                        "scope_adjusted_loan_value": scope_adjusted_loan_value,
                        "scope_adjusted_focf_debt": scope_adjusted_focf_debt,
                        "liquidity": liquidity,
                    })
                raw_data["scope_credit_metrics"] = credit_metrics

        LOGGER.debug("Parsed raw data keys: %s", sorted(raw_data.keys()))
        return raw_data
    except Exception as e:
        LOGGER.exception("Error while parsing %s", file_path)
        _, _, tb = sys.exc_info()
        LOGGER.error("Parser failure line number: %s", tb.tb_lineno if tb else "unknown")
        raise Exception(e)
