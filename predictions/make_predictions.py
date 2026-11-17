import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

# LOAD DATA ----------------------------------------------------------

df = pd.read_csv("cleaned_datasets/main_data.csv") 
indicies_df = pd.read_csv("cleaned_datasets/overall/risk_index_monthly.csv")

# CLEAN DATA AND ADD COLUMNS -------------------------------------


def clean_data(
    X_df,
    y_df,
    target_col="index_equal",
    forecast_months=6,
    prediction_start="2026-06",
    prediction_end="2026-11",
    feature_lags=[1, 2, 3],
    index_lags=[1, 3, 6],
    selected_cols=None,
    split=0.9,
    save_files=False
):
    # Make copies
    X_df = X_df.copy()
    y_df = y_df[["Month", target_col]].copy()

    # Convert dates to monthly periods
    X_df["Month"] = pd.to_datetime(X_df["Month"]).dt.to_period("M")
    y_df["Month"] = pd.to_datetime(y_df["Month"]).dt.to_period("M")

    # Sort before generating lagged features
    X_df = X_df.sort_values("Month").reset_index(drop=True)
    y_df = y_df.sort_values("Month").reset_index(drop=True)

    # Select columns to use as features
    if selected_cols is None:
        selected_cols = X_df.select_dtypes(include=np.number).columns.tolist()

    # Validate selected columns
    missing_cols = [col for col in selected_cols if col not in X_df.columns]

    if missing_cols:
        raise ValueError(f"Columns not found in X_df: {missing_cols}")

    non_numeric_cols = [
        col for col in selected_cols
        if not pd.api.types.is_numeric_dtype(X_df[col])
    ]

    if non_numeric_cols:
        raise ValueError(f"Selected columns must be numeric: {non_numeric_cols}")

    # Keep only selected columns and Month
    X_df = X_df[["Month"] + selected_cols].copy()

    # Generate new features from selected columns
    new_features = {}

    for col in selected_cols:
        for lag in feature_lags:
            if "SANC" in col or "CPI" in col:
                new_features[f"{col}_change_{lag}m"] = (
                    X_df[col] - X_df[col].shift(lag)
                )
            else:
                new_features[f"{col}_pct_change_{lag}m"] = (
                    X_df[col].pct_change(
                        periods=lag, fill_method=None
                    ) * 100
                )

    X_df = pd.concat(
        [X_df, pd.DataFrame(new_features, index=X_df.index)],
        axis=1
    )

    # --------------------------------------------------
    # Prepare GPR values from one month before target
    # --------------------------------------------------

    current_gpr = X_df[["Month"] + [
        col for col in ["GPR_RUS", "GPR_CHN"]
        if col in X_df.columns
    ]].copy()

    for col in ["GPR_RUS", "GPR_CHN"]:
        if col not in current_gpr.columns:
            continue

        for lag in index_lags:
            current_gpr[f"{col}_pct_change_{lag}m"] = (
                current_gpr[col].pct_change(
                    periods=lag, fill_method=None
                ) * 100
            )

    gpr_rename = {
        col: f"{col}_prev_month"
        for col in ["GPR_RUS", "GPR_CHN"]
        if col in current_gpr.columns
    }

    for col in ["GPR_RUS", "GPR_CHN"]:
        if col not in current_gpr.columns:
            continue

        for lag in index_lags:
            gpr_rename[f"{col}_pct_change_{lag}m"] = (
                f"{col}_prev_month_pct_change_{lag}m"
            )

    current_gpr = current_gpr.rename(columns=gpr_rename)
    current_gpr["Month"] += 1

    # --------------------------------------------------
    # Prepare previous-month risk-index features
    # --------------------------------------------------

    previous_index = y_df.copy()

    for lag in index_lags:
        previous_index[f"index_pct_change_{lag}m"] = (
            previous_index[target_col].pct_change(
                periods=lag, fill_method=None
            ) * 100
        )

    previous_index = previous_index.rename(columns={
        "Month": "target_month",
        target_col: "previous_month_index"
    })

    previous_index["target_month"] += 1

    # --------------------------------------------------
    # Align features with target months
    # --------------------------------------------------

    X_df["target_month"] = X_df["Month"] + forecast_months

    X_df["month_num"] = X_df["target_month"].dt.month

    X_df["month_sin"] = np.sin(
        2 * np.pi * X_df["month_num"] / 12
    )

    X_df["month_cos"] = np.cos(
        2 * np.pi * X_df["month_num"] / 12
    )

    # Match features to target month
    data = X_df.merge(
        y_df,
        left_on="target_month",
        right_on="Month",
        how="left",
        suffixes=("_feature", "_target")
    )

    # Add previous-month GPR
    data = data.merge(
        current_gpr,
        left_on="target_month",
        right_on="Month",
        how="left"
    )

    # Add previous-month risk index
    data = data.merge(
        previous_index,
        on="target_month",
        how="left"
    )

    # --------------------------------------------------
    # Duplicate important features
    # --------------------------------------------------

    important_features = [
        "previous_month_index",
        "GPR_RUS_prev_month",
        "GPR_CHN_prev_month"
    ]

    important_features = [
        col for col in important_features if col in data.columns
    ]

    for i in range(1, 5):
        for col in important_features:
            suffix = "" if i == 1 else str(i)
            data[f"{col}_weighted{suffix}"] = data[col]

    data = data.sort_values("target_month").reset_index(drop=True)

    # --------------------------------------------------
    # Identify feature columns
    # --------------------------------------------------

    exclude_cols = [
        "Month_feature",
        "target_month",
        "Month_target",
        "Month",
        target_col
    ]

    feature_cols = [
        col for col in data.select_dtypes(include=np.number).columns
        if col not in exclude_cols
    ]

    # --------------------------------------------------
    # Separate training and prediction data
    # --------------------------------------------------

    train_data = data[data[target_col].notna()].copy()

    prediction_start = pd.Period(prediction_start, freq="M")
    prediction_end = pd.Period(prediction_end, freq="M")

    prediction_data = data[
        (data[target_col].isna()) &
        (data["target_month"] >= prediction_start) &
        (data["target_month"] <= prediction_end)
    ].copy()

    X = train_data[feature_cols].replace(
        [np.inf, -np.inf], np.nan
    )

    y = train_data[target_col]

    X_future = prediction_data[feature_cols].replace(
        [np.inf, -np.inf], np.nan
    )

    # --------------------------------------------------
    # Chronological split
    # --------------------------------------------------

    split = int(len(X) * split)

    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    # --------------------------------------------------
    # Optional saving
    # --------------------------------------------------

    if save_files:
        data.to_csv(f"features_{target_col}.csv", index=False)
        prediction_data.to_csv(
            f"future_{target_col}.csv", index=False
        )

    return {
        "data": data,
        "train_data": train_data,
        "prediction_data": prediction_data,
        "feature_cols": feature_cols,
        "X": X,
        "y": y,
        "X_future": X_future,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }


results_equal = clean_data(
    df, indicies_df,
    target_col="index_equal"
)

X_train = results_equal["X_train"]
X_test = results_equal["X_test"]

y_train = results_equal["y_train"]
y_test = results_equal["y_test"]

X_future = results_equal["X_future"]
data = results_equal["data"]

prediction_data = results_equal["prediction_data"]
feature_cols = results_equal["feature_cols"]

# PLOTTING FUNCTION -------------------------------------

def plot_accuracy(
    name,
    train_predictions,
    test_predictions,
    y_train,
    y_test,
    model_data
):
    # Get dates
    train_dates = model_data.loc[
        y_train.index, "target_month"
    ].dt.to_timestamp()

    test_dates = model_data.loc[
        y_test.index, "target_month"
    ].dt.to_timestamp()

    plt.figure(figsize=(14, 6))

    # Training data
    plt.plot(
        train_dates, y_train.values,
        label="Actual Training", alpha=0.7
    )

    plt.plot(
        train_dates, train_predictions,
        label="Predicted Training", linestyle="--"
    )

    # Testing data
    plt.plot(
        test_dates, y_test.values,
        label="Actual Testing", alpha=0.7
    )

    plt.plot(
        test_dates, test_predictions,
        label="Predicted Testing", linestyle="--"
    )

    plt.xlabel("Date")
    plt.ylabel("Risk Index")
    plt.title(f"{name}: Actual vs. Predicted Risk Index")

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    plt.ylim(0, 100)
    plt.yticks(range(0, 101, 10))

    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"predictions/graphs/{name}.png")


# OVERALL XGBOOST DECISION TREE MODEL ----------------------------------

model_xgb = XGBRegressor(
    n_estimators=1000,
    max_depth=3,
    learning_rate=0.1,
    subsample=0.6,
    colsample_bytree=0.7, 
    min_child_weight=3, 
    reg_lambda=10,
    reg_alpha=1,
    gamma=0.5,
    objective="reg:squarederror",
    eval_metric="rmse",
    early_stopping_rounds=50,
    random_state=42,
    n_jobs=-1
)

# Reserve the latest 10% of training data for validation
val_split = int(len(X_train) * 0.9)

X_fit = X_train.iloc[:val_split]
X_val = X_train.iloc[val_split:]

y_fit = y_train.iloc[:val_split]
y_val = y_train.iloc[val_split:]

model_xgb.fit(X_fit, y_fit, eval_set=[(X_val, y_val)], verbose=False)

predictions = model_xgb.predict(X_test)

print("MAE OVERALL:", mean_absolute_error(y_test, predictions))
print("RMSE OVERALL:", np.sqrt(mean_squared_error(y_test, predictions)))
print("R^2 OVERALL:", r2_score(y_test, predictions))

train_predictions = model_xgb.predict(X_train)
test_predictions = model_xgb.predict(X_test)

# Keep predictions within the risk index range
train_predictions = np.clip(train_predictions, 0, 100)
test_predictions = np.clip(test_predictions, 0, 100)

plot_accuracy(
    "XGBoost - Overall Risk Index",
    train_predictions,
    test_predictions,
    y_train,
    y_test,
    results_equal["data"]
)

# MAE OVERALL: 2.6799317839249333
# RMSE OVERALL: 3.1585740835813656
# R^2 OVERALL: -0.22822303566990065

# OVERALL FUTURE PREDICTIONS -------------------------------------


def recursive_forecast(
    model,
    X_future,
    prediction_data,
    previous_index_duplicates=1
):
    # Make a copy of future features
    X_future_recursive = X_future.copy()

    # Sort future predictions chronologically
    future_order = prediction_data.loc[
        X_future_recursive.index, "target_month"
    ].sort_values().index

    X_future_recursive = X_future_recursive.loc[future_order]

    # Identify previous-index columns
    previous_index_columns = [
        "previous_month_index"
    ] + [
        f"previous_month_index_weighted{'' if i == 1 else i}"
        for i in range(1, previous_index_duplicates + 1)
    ]

    # Keep only columns that exist
    previous_index_columns = [
        col for col in previous_index_columns
        if col in X_future_recursive.columns
    ]

    recursive_predictions = []
    previous_prediction = None

    for i in range(len(X_future_recursive)):

        row_index = X_future_recursive.index[i]

        # Update previous-index features with the last prediction
        if previous_prediction is not None:
            for col in previous_index_columns:
                X_future_recursive.loc[row_index, col] = (
                    previous_prediction
                )

        # Predict current month
        prediction = model.predict(
            X_future_recursive.loc[[row_index]]
        )[0]

        prediction = np.clip(prediction, 0, 100)

        recursive_predictions.append(prediction)

        # Use this prediction for the next month
        previous_prediction = prediction

    future_results = prediction_data.loc[
        X_future_recursive.index, ["target_month"]
    ].copy()

    future_results["predicted_index"] = recursive_predictions

    return future_results, X_future_recursive

future_results, X_future_recursive = recursive_forecast(
    model_xgb,
    results_equal["X_future"],
    results_equal["prediction_data"],
)

recursive_predictions = future_results["predicted_index"].tolist()

print("Overall Future Predictions")
print(future_results)
print("\n")

# Predictions
train_predictions = model_xgb.predict(X_train)
test_predictions = model_xgb.predict(X_test)

# Keep predictions within the 0-100 index range
train_predictions = np.clip(train_predictions, 0, 100)
test_predictions = np.clip(test_predictions, 0, 100)
recursive_predictions = np.clip(recursive_predictions, 0, 100)

# Get dates for each dataset
train_dates = data.loc[X_train.index, "target_month"].dt.to_timestamp()
test_dates = data.loc[X_test.index, "target_month"].dt.to_timestamp()
future_dates = prediction_data.loc[X_future.index, "target_month"].dt.to_timestamp()

# Create graph
plt.figure(figsize=(16, 7))

# Training
plt.plot(
    train_dates, y_train,
    label="Training Actual",
    linewidth=2
)
plt.plot(
    train_dates, train_predictions,
    label="Training Predicted",
    linestyle="--"
)

# Testing
plt.plot(
    test_dates, y_test,
    label="Testing Actual",
    linewidth=2
)
plt.plot(
    test_dates, test_predictions,
    label="Testing Predicted",
    linestyle="--"
)

# Latest months (future predictions)
plt.plot(
    future_dates, recursive_predictions,
    label="Recent Predictions",
    linewidth=2
)

# Formatting
plt.xlabel("Date")
plt.ylabel("Risk Index")
plt.title("XGBoost: Actual vs. Predicted Russia-China Risk Index")


plt.ylim(0, 100)
plt.yticks(range(0, 101, 10))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.xticks(rotation=45)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("predictions/graphs/overall_predictions.png")

# RUSSIA XGBOOST DECISION TREE MODEL -------------------------------------

# Load Russia risk index
rus_ind_df = pd.read_csv("cleaned_datasets/russia/risk_index_monthly.csv")

# Clean and prepare data
results_rus = clean_data(df, rus_ind_df)

# Create a separate copy of the old XGBoost model
xgb_rus = XGBRegressor(
    n_estimators=1000,
    max_depth=3,
    learning_rate=0.1,
    subsample=.9,
    colsample_bytree=1,
    min_child_weight=3,
    reg_lambda=10,
    reg_alpha=1,
    gamma=0.5,
    objective="reg:squarederror",
    eval_metric="rmse",
    early_stopping_rounds=50,
    random_state=42,
    n_jobs=-1
)

# Chronological validation split for early stopping
val_split = int(len(results_rus["X_train"]) * 0.9)

X_fit = results_rus["X_train"].iloc[:val_split]
X_val = results_rus["X_train"].iloc[val_split:]

y_fit = results_rus["y_train"].iloc[:val_split]
y_val = results_rus["y_train"].iloc[val_split:]

# Fit model
xgb_rus.fit(
    X_fit,
    y_fit,
    eval_set=[(X_val, y_val)],
    verbose=False
)

# Generate predictions
rus_train_predictions = xgb_rus.predict(results_rus["X_train"])
rus_test_predictions = xgb_rus.predict(results_rus["X_test"])

print("MAE RUSSIA:", mean_absolute_error(results_rus["y_test"], rus_test_predictions))
print("RMSE RUSSIA:", np.sqrt(mean_squared_error(results_rus["y_test"], rus_test_predictions)))
print("R^2 RUSSIA:", r2_score(results_rus["y_test"], rus_test_predictions))

# Plot accuracy
plot_accuracy(
    "XGBoost - Russia Risk Index",
    rus_train_predictions,
    rus_test_predictions,
    results_rus["y_train"],
    results_rus["y_test"],
    results_rus["data"]
)

# MAE: 3.7567280008067256
# RMSE: 4.473194329068692
# R²: 0.2024666817981554

# RUSSIA FUTURE PREDICTIONS -------------------------------------

# ============================================================
# RUSSIA: RECURSIVE XGBOOST FORECAST
# ============================================================

future_results_rus, X_future_recursive_rus = recursive_forecast(
    xgb_rus,
    results_rus["X_future"],
    results_rus["prediction_data"],
)

recursive_predictions_rus = future_results_rus["predicted_index"].tolist()

print("Russia Future Predictions")
print(future_results_rus)
print("\n")

# ============================================================
# TRAINING AND TESTING PREDICTIONS
# ============================================================

X_train_rus = results_rus["X_train"]
X_test_rus = results_rus["X_test"]
data_rus = results_rus["data"]
prediction_data_rus = results_rus["prediction_data"]

y_train_rus = results_rus["y_train"]
y_test_rus = results_rus["y_test"]

train_predictions_rus = xgb_rus.predict(X_train_rus)
test_predictions_rus = xgb_rus.predict(X_test_rus)

# Keep predictions within the 0-100 index range
train_predictions_rus = np.clip(train_predictions_rus, 0, 100)
test_predictions_rus = np.clip(test_predictions_rus, 0, 100)
recursive_predictions_rus = np.clip(
    recursive_predictions_rus, 0, 100
)

# ============================================================
# GET DATES
# ============================================================

train_dates_rus = data_rus.loc[
    X_train_rus.index, "target_month"
].dt.to_timestamp()

test_dates_rus = data_rus.loc[
    X_test_rus.index, "target_month"
].dt.to_timestamp()

future_dates_rus = prediction_data_rus.loc[
    X_future_recursive_rus.index, "target_month"
].dt.to_timestamp()

# ============================================================
# CREATE GRAPH
# ============================================================

plt.figure(figsize=(16, 7))

# Training
plt.plot(
    train_dates_rus,
    y_train_rus,
    label="Training Actual",
    linewidth=2
)

plt.plot(
    train_dates_rus,
    train_predictions_rus,
    label="Training Predicted",
    linestyle="--"
)

# Testing
plt.plot(
    test_dates_rus,
    y_test_rus,
    label="Testing Actual",
    linewidth=2
)

plt.plot(
    test_dates_rus,
    test_predictions_rus,
    label="Testing Predicted",
    linestyle="--"
)

# Future predictions
plt.plot(
    future_dates_rus,
    recursive_predictions_rus,
    label="Future Predictions",
    linewidth=2
)

# Formatting
plt.xlabel("Date")
plt.ylabel("Risk Index")
plt.title("XGBoost: Russia Risk Index Forecast")

plt.ylim(0, 100)
plt.yticks(range(0, 101, 10))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.xticks(rotation=45)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("predictions/graphs/russia_predictions.png")

# CHINA XGBOOST DECISION TREE MODEL -------------------------------------

# Load China risk index
chn_ind_df = pd.read_csv("cleaned_datasets/china/risk_index_monthly.csv")

# Clean and prepare data
results_chn = clean_data(df, chn_ind_df)

# XGBoost model
xgb_chn = XGBRegressor(
    n_estimators=1000,
    max_depth=2,
    learning_rate=0.1,
    subsample=.7, 
    colsample_bytree=.6,
    min_child_weight=4,
    reg_lambda=10,
    reg_alpha=1,
    gamma=0.5,
    objective="reg:squarederror",
    eval_metric="rmse",
    early_stopping_rounds=50,
    random_state=42,
    n_jobs=-1
)

# Chronological validation split for early stopping
val_split = int(len(results_chn["X_train"]) * 0.9)

X_fit = results_chn["X_train"].iloc[:val_split]
X_val = results_chn["X_train"].iloc[val_split:]

y_fit = results_chn["y_train"].iloc[:val_split]
y_val = results_chn["y_train"].iloc[val_split:]

# Fit model
xgb_chn.fit(
    X_fit,
    y_fit,
    eval_set=[(X_val, y_val)],
    verbose=False
)

# Generate predictions
chn_train_predictions = xgb_chn.predict(results_chn["X_train"])
chn_test_predictions = xgb_chn.predict(results_chn["X_test"])

print("MAE CHINA:", mean_absolute_error(results_chn["y_test"], chn_test_predictions))
print("RMSE CHINA:", np.sqrt(mean_squared_error(results_chn["y_test"], chn_test_predictions)))
print("R^2 CHINA:", r2_score(results_chn["y_test"], chn_test_predictions))

# Plot accuracy
plot_accuracy(
    "XGBoost - China Risk Index",
    chn_train_predictions,
    chn_test_predictions,
    results_chn["y_train"],
    results_chn["y_test"],
    results_chn["data"]
)

# MAE CHINA: 4.8061157173488445
# RMSE CHINA: 5.565631161967663
# R^2 CHINA: -0.935692396649729

# CHINA FUTURE PREDICTIONS -------------------------------------

# ============================================================
# CHINA: RECURSIVE XGBOOST FORECAST
# ============================================================

# Make a copy of future features

future_results_chn, X_future_recursive_chn = recursive_forecast(
    xgb_chn,
    results_chn["X_future"],
    results_chn["prediction_data"],
)

recursive_predictions_chn = future_results_chn["predicted_index"].tolist()

print("China Future Predictions")
print(future_results_chn)
print("\n")


# ============================================================
# TRAINING AND TESTING PREDICTIONS
# ============================================================

X_train_chn = results_chn["X_train"]
X_test_chn = results_chn["X_test"]
data_chn = results_chn["data"]
prediction_data_chn = results_chn["prediction_data"]

y_train_chn = results_chn["y_train"]
y_test_chn = results_chn["y_test"]

train_predictions_chn = xgb_chn.predict(X_train_chn)
test_predictions_chn = xgb_chn.predict(X_test_chn)

# Keep predictions within the 0-100 index range
train_predictions_chn = np.clip(train_predictions_chn, 0, 100)
test_predictions_chn = np.clip(test_predictions_chn, 0, 100)
recursive_predictions_chn = np.clip(
    recursive_predictions_chn, 0, 100
)


# ============================================================
# GET DATES
# ============================================================

train_dates_chn = data_chn.loc[
    X_train_chn.index, "target_month"
].dt.to_timestamp()

test_dates_chn = data_chn.loc[
    X_test_chn.index, "target_month"
].dt.to_timestamp()

future_dates_chn = prediction_data_chn.loc[
    X_future_recursive_chn.index, "target_month"
].dt.to_timestamp()


# ============================================================
# CREATE GRAPH
# ============================================================

plt.figure(figsize=(16, 7))

# Training
plt.plot(
    train_dates_chn,
    y_train_chn,
    label="Training Actual",
    linewidth=2
)

plt.plot(
    train_dates_chn,
    train_predictions_chn,
    label="Training Predicted",
    linestyle="--"
)

# Testing
plt.plot(
    test_dates_chn,
    y_test_chn,
    label="Testing Actual",
    linewidth=2
)

plt.plot(
    test_dates_chn,
    test_predictions_chn,
    label="Testing Predicted",
    linestyle="--"
)

# Future predictions
plt.plot(
    future_dates_chn,
    recursive_predictions_chn,
    label="Future Predictions",
    linewidth=2
)

# Formatting
plt.xlabel("Date")
plt.ylabel("Risk Index")
plt.title("XGBoost: China Risk Index Forecast")

plt.ylim(0, 100)
plt.yticks(range(0, 101, 10))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.xticks(rotation=45)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("predictions/graphs/china_predictions.png")

# CREATE FILE WITH VARIABLES AND PREDICTION INDEX ----------------------------------

def add_index_predictions(
    original_df,
    results,
    model,
    future_predictions,
    target_col,
    prefix
):
    # Historical data
    train_data = results["train_data"].copy()

    # Get historical model predictions
    historical_predictions = model.predict(results["X"])

    # Map historical predictions to their target months
    predicted_df = pd.DataFrame({
        "Month": train_data["target_month"].values,
        f"{prefix}_predicted_future": historical_predictions
    })

    # Get future target months in chronological order
    future_data = results["prediction_data"].copy()
    future_data = future_data.sort_values("target_month")

    # Match future predictions to their target months
    future_df = pd.DataFrame({
        "Month": future_data["target_month"].values,
        f"{prefix}_future": future_predictions
    })

    # Actual historical index values
    actual_df = train_data[["target_month", target_col]].copy()
    actual_df = actual_df.rename(columns={
        "target_month": "Month",
        target_col: f"{prefix}_actual_future"
    })

    # Combine actual historical values with future predictions
    actual_future_df = actual_df.merge(
        future_df,
        on="Month",
        how="outer"
    )

    actual_future_df[f"{prefix}_actual_future"] = (
        actual_future_df[f"{prefix}_actual_future"].fillna(
            actual_future_df[f"{prefix}_future"]
        )
    )

    actual_future_df = actual_future_df[
        ["Month", f"{prefix}_actual_future"]
    ]

    # Combine historical model predictions with future predictions
    predicted_future_df = predicted_df.merge(
        future_df,
        on="Month",
        how="outer"
    )

    predicted_future_df[f"{prefix}_predicted_future"] = (
        predicted_future_df[f"{prefix}_predicted_future"].fillna(
            predicted_future_df[f"{prefix}_future"]
        )
    )

    predicted_future_df = predicted_future_df[
        ["Month", f"{prefix}_predicted_future"]
    ]

    # Combine both sets of columns
    index_df = actual_future_df.merge(
        predicted_future_df,
        on="Month",
        how="outer"
    )

    # Merge into original dataset
    original_df = original_df.copy()
    original_df["Month"] = pd.PeriodIndex(
        original_df["Month"], freq="M"
    )

    original_df = original_df.merge(
        index_df,
        on="Month",
        how="outer"
    )

    return original_df

# Overall index
future_equal_predictions = recursive_predictions

# Russia index
future_rus_predictions = recursive_predictions_rus

# China index
future_chn_predictions = recursive_predictions_chn

# Overall
export_df = add_index_predictions(
    df,
    results_equal,
    model_xgb,
    future_equal_predictions,
    "index_equal",
    "overall"
)

# Russia
export_df = add_index_predictions(
    export_df,
    results_rus,
    xgb_rus,
    future_rus_predictions,
    "index_equal",
    "russia"
)

# China
export_df = add_index_predictions(
    export_df,
    results_chn,
    xgb_chn,
    future_chn_predictions,
    "index_equal",
    "china"
)

export_df["Month"] = export_df["Month"].dt.to_timestamp()

export_df = export_df.sort_values("Month").reset_index(drop=True)

overall_df = pd.read_csv("cleaned_datasets/overall_data.csv")

# Select only Month and the six prediction columns
prediction_cols = [
    "overall_actual_future",
    "overall_predicted_future",
    "russia_actual_future",
    "russia_predicted_future",
    "china_actual_future",
    "china_predicted_future"
]

predictions = export_df[["Month"] + prediction_cols].copy()

# Make sure both Month columns have the same format
overall_df["Month"] = pd.to_datetime(overall_df["Month"]).dt.to_period("M")
predictions["Month"] = pd.to_datetime(predictions["Month"]).dt.to_period("M")

# Merge predictions into overall_df
overall_df = overall_df.merge(
    predictions,
    on="Month",
    how="outer"
)

# Sort chronologically
overall_df = overall_df.sort_values("Month").reset_index(drop=True)

# Convert Month back to datetime
overall_df["Month"] = overall_df["Month"].dt.to_timestamp()

# Export
overall_df.to_csv(
    "overall_data_with_predictions.csv",
    index=False
)