
import io
import os
from pathlib import Path

import boto3
import pandas as pd
import streamlit as st
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    ProfileNotFound,
)


# ============================================================
# 1. Streamlit page configuration
# ============================================================

st.set_page_config(
    page_title="PharmaFlow Analytics",
    page_icon="💊",
    layout="wide",
)


# ============================================================
# 2. Data source configuration
# ============================================================

# Supported modes:
# local - Load Gold-layer Parquet files from the repository
# s3    - Load Gold-layer Parquet files from AWS S3
#
# Default to local mode for public portfolio deployment.
# Existing AWS deployments can set PHARMAFLOW_DATA_SOURCE=s3.

DATA_SOURCE = os.getenv(
    "PHARMAFLOW_DATA_SOURCE",
    "local",
).strip().lower()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_GOLD_DIR = PROJECT_ROOT / "data" / "gold"

BUCKET = os.getenv(
    "PHARMAFLOW_S3_BUCKET",
    "pharmaflow-data-673502297238-eu-west-2",
)

REGION = os.getenv(
    "AWS_DEFAULT_REGION",
    "eu-west-2",
)

# Local AWS access: AWS_PROFILE=pharmaflow-dev
# EC2 IAM role: leave AWS_PROFILE unset.
PROFILE = os.getenv("AWS_PROFILE")

DATASETS = {
    "Branches": "gold/branch_revenue.parquet",
    "Medicines": "gold/medicine_revenue.parquet",
    "Suppliers": "gold/supplier_spend.parquet",
}


# ============================================================
# 3. AWS S3 Gold-layer data loader
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner="Loading Gold-layer data from AWS S3...",
)
def load_gold_data(bucket, region, profile):
    session = boto3.Session(
        region_name=region,
        **({"profile_name": profile} if profile else {}),
    )

    client = session.client("s3")
    results = {}

    for name, key in DATASETS.items():
        response = client.get_object(
            Bucket=bucket,
            Key=key,
        )

        content = response["Body"].read()

        results[name] = pd.read_parquet(
            io.BytesIO(content)
        )

    return results


# ============================================================
# 4. Local Gold-layer data loader
# ============================================================

@st.cache_data(
    show_spinner="Loading local Gold-layer datasets...",
)
def load_local_gold_data():
    results = {}

    for name, key in DATASETS.items():
        file_path = PROJECT_ROOT / "data" / key

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Missing Gold-layer dataset: {file_path}"
            )

        results[name] = pd.read_parquet(file_path)

    return results


# ============================================================
# 5. Data analysis helper functions
# ============================================================

def numeric_columns(df):
    return df.select_dtypes(
        include="number"
    ).columns.tolist()


def dimension_columns(df):
    return [
        column
        for column in df.columns
        if not pd.api.types.is_numeric_dtype(
            df[column]
        )
    ]


def preferred_column(columns, keywords):
    for keyword in keywords:
        for column in columns:
            if keyword in column.lower():
                return column

    return columns[0] if columns else None


# ============================================================
# 6. Reusable analytics component
# ============================================================

def render_analysis(
    title,
    df,
    metric_keywords,
    dimension_keywords,
):
    st.subheader(title)

    if df.empty:
        st.info("No records are available.")
        return

    measures = numeric_columns(df)
    dimensions = dimension_columns(df)

    if not measures:
        st.dataframe(
            df,
            width="stretch",
        )
        return

    # Exclude numeric identifier columns where possible.
    business_measures = [
        column
        for column in measures
        if not column.lower().endswith("_id")
    ]

    if business_measures:
        measures = business_measures

    default_metric = preferred_column(
        measures,
        metric_keywords,
    )

    left, right = st.columns(2)

    with left:
        metric = st.selectbox(
            "Measure",
            measures,
            index=measures.index(default_metric),
            key=f"{title}_metric",
        )

    with right:
        if dimensions:
            default_dimension = preferred_column(
                dimensions,
                dimension_keywords,
            )

            dimension = st.selectbox(
                "Group by",
                dimensions,
                index=dimensions.index(
                    default_dimension
                ),
                key=f"{title}_dimension",
            )
        else:
            dimension = None

    if dimension:
        chart_data = (
            df.groupby(
                dimension,
                dropna=False,
            )[metric]
            .sum()
            .sort_values(ascending=False)
            .head(15)
        )

        st.bar_chart(
            chart_data,
            horizontal=True,
        )
    else:
        st.metric(
            "Total",
            f"{df[metric].sum():,.2f}",
        )

    with st.expander("View source data"):
        st.dataframe(
            df,
            width="stretch",
        )


# ============================================================
# 7. Dashboard header
# ============================================================

st.title("💊 PharmaFlow Analytics Dashboard")

st.caption(
    "Pharmacy Retail & Wholesale | "
    "Apache Airflow • AWS S3 • Bronze/Silver/Gold"
)

st.caption(
    "Interactive analytics powered by synthetic "
    "pharmacy retail and wholesale datasets."
)


# ============================================================
# 8. Sidebar
# ============================================================

with st.sidebar:
    st.header("Data Source")

    if DATA_SOURCE == "local":
        st.success("Local Gold-layer data")

        st.write(
            "Storage:",
            "Parquet files",
        )

        st.write(
            "Mode:",
            "Public portfolio demonstration",
        )

    elif DATA_SOURCE == "s3":
        st.info("AWS S3 Gold-layer data")

        st.write(
            "AWS Region:",
            REGION,
        )

        st.write(
            "S3 Bucket:",
            BUCKET,
        )

        if PROFILE:
            st.write(
                "Authentication:",
                f"AWS Profile ({PROFILE})",
            )
        else:
            st.write(
                "Authentication:",
                "AWS Default Credential Chain",
            )

    else:
        st.error("Unsupported data source.")

    if st.button(
        "Refresh data",
        width="stretch",
    ):
        load_gold_data.clear()
        load_local_gold_data.clear()
        st.rerun()

    st.divider()

    st.caption(
        "PharmaFlow Data Engineering Platform"
    )


# ============================================================
# 9. Load selected data source
# ============================================================

try:
    if DATA_SOURCE == "local":
        datasets = load_local_gold_data()

    elif DATA_SOURCE == "s3":
        datasets = load_gold_data(
            BUCKET,
            REGION,
            PROFILE,
        )

    else:
        raise ValueError(
            "PHARMAFLOW_DATA_SOURCE must be "
            "'local' or 's3'."
        )

except (
    BotoCoreError,
    ClientError,
    ProfileNotFound,
    NoCredentialsError,
    FileNotFoundError,
    OSError,
    ValueError,
    ImportError,
) as error:
    st.error(
        "Unable to load PharmaFlow Gold-layer datasets."
    )

    # Keep internal file paths and AWS error details
    # out of the publicly hosted dashboard.
    if os.getenv(
        "PHARMAFLOW_DEBUG",
        "false",
    ).lower() == "true":
        st.code(str(error))
    else:
        st.info(
            "The analytics datasets are currently "
            "unavailable. Please try again later."
        )

    st.stop()


# ============================================================
# 10. Extract loaded datasets
# ============================================================

branches = datasets["Branches"]
medicines = datasets["Medicines"]
suppliers = datasets["Suppliers"]


# ============================================================
# 11. Dashboard summary metrics
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Pharmacy Branches",
        f"{len(branches):,}",
    )

with col2:
    st.metric(
        "Medicine Categories / Products",
        f"{len(medicines):,}",
    )

with col3:
    st.metric(
        "Suppliers",
        f"{len(suppliers):,}",
    )


# ============================================================
# 12. Analytics dashboard tabs
# ============================================================

st.divider()

tab1, tab2, tab3 = st.tabs(
    [
        "Branch Revenue",
        "Medicine Revenue",
        "Supplier Spending",
    ]
)

with tab1:
    render_analysis(
        "Revenue by Pharmacy Branch",
        branches,
        ["revenue", "total", "sales"],
        ["branch_name", "branch"],
    )

with tab2:
    render_analysis(
        "Revenue by Medicine",
        medicines,
        ["revenue", "total", "sales"],
        ["medicine_name", "medicine"],
    )

with tab3:
    render_analysis(
        "Wholesale Spending by Supplier",
        suppliers,
        ["spend", "cost", "total"],
        ["supplier_name", "supplier"],
    )


# ============================================================
# 13. Footer
# ============================================================

st.divider()

st.caption(
    "PharmaFlow Data Engineering Platform | "
    "Synthetic pharmacy data for portfolio demonstration"
)
