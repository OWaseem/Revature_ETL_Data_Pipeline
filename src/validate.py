import pandas as pd


def validate(df, source_name, rules):
    valid_rows = []
    rejected_rows = []

    for _, row in df.iterrows():
        passed = True
        for rule in rules:
            column = rule["column"]
            condition = rule["condition"]
            value = row[column]
            if not eval(condition, {"value": value, "pd": pd}):
                rejected_rows.append({
                    "source_name": source_name,
                    "raw_payload": row.to_dict(),
                    "reason": f"{column} failed: {condition}"
                })
                passed = False
                break
        if passed:
            valid_rows.append(row)

    valid_df = pd.DataFrame(valid_rows)
    rejects_df = pd.DataFrame(rejected_rows)

    return valid_df, rejects_df
