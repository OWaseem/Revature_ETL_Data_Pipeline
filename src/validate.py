import pandas as pd
from rules import rules


def validate(df, source):
    source_rules = rules.get(source, [])
    valid_rows = []
    rejected_rows = []

    for _, row in df.iterrows():
        passed = True
        for rule in source_rules:
            column = rule["column"]
            condition = rule["condition"]
            value = row[column]
            if not eval(condition):
                rejected_rows.append({
                    "source_name": source,
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
