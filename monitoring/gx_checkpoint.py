import great_expectations as gx
import pandas as pd

context = gx.get_context()

df = pd.read_csv("/opt/airflow/cleaned_prices.csv")

print(f"Fichier chargé: {len(df)} lignes")
print(f"Colonnes: {list(df.columns)}")

datasource = context.sources.add_pandas("price_data")
asset = datasource.add_dataframe_asset("cleaned_prices")
batch = asset.build_batch_request(dataframe=df)

try:
    context.delete_expectation_suite("price_suite")
except:
    pass
suite = context.add_expectation_suite("price_suite")

validator = context.get_validator(
    batch_request=batch,
    expectation_suite_name="price_suite"
)

price_col = "price" if "price" in df.columns else "price_mad"

validator.expect_column_to_exist(price_col)
validator.expect_column_values_to_not_be_null(price_col)
validator.expect_column_values_to_be_between(
    price_col,
    min_value=0,
    max_value=10000
)

if "source" in df.columns:
    validator.expect_column_values_to_be_in_set(
        "source",
        ["jumia", "marjane", "micromagma", "zara", "avito"]
    )

if "name" in df.columns:
    validator.expect_column_values_to_not_be_null("name")

validator.save_expectation_suite()

checkpoint = context.add_or_update_checkpoint(
    name="price_checkpoint",
    validations=[{
        "batch_request": batch,
        "expectation_suite_name": "price_suite"
    }]
)

results = checkpoint.run()

if results["success"]:
    print("Data quality PASSED - toutes les regles respectees")
else:
    print("Data quality FAILED - voir les details:")
    for result in results["run_results"].values():
        for r in result["validation_result"]["results"]:
            if not r["success"]:
                print(f"  ECHEC: {r['expectation_config']['expectation_type']}")