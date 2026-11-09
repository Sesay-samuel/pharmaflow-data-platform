
import io
import os

import boto3
import pandas as pd
import streamlit as st
from botocore.exceptions import BotoCoreError, ClientError, ProfileNotFound, NoCredentialsError


st.set_page_config(
    page_title="PharmaFlow Analytics",
    page_icon="💊",
    layout="wide",
)

BUCKET = os.getenv(
    "PHARMAFLOW_S3_BUCKET",
    "pharmaflow-data-673502297238-eu-west-2",
)

REGION = os.getenv("AWS_DEFAULT_REGION", "eu-west-2")

# Local: use AWS_PROFILE=pharmaflow-dev
# EC2: leave AWS_PROFILE unset to use the attached IAM role.
PROFILE = os.getenv("AWS_PROFILE")

DATASETS = {
    "Branches": "gold/branch_revenue.parquet",
    "Medicines": "gold/medicine_revenue.parquet",
    "Suppliers": "gold/supplier_spend.parquet",
}


@st.cache_data(ttl=300, show_spinner="Loading Gold data from S3...")
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
        results[name] = pd.read_parquet(io.BytesIO(content))

    return results


def numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()


def dimension_columns(df):
    return [
        column
        for column in df.columns
        if not pd.api.types.is_numeric_dtype(df[column])
    ]


def preferred_column(columns, keywords):
    for keyword in keywords:
        for column in columns:
            if keyword in column.lower():
                return column

    return columns[0] if columns else None


def render_analysis(title, df, metric_keywords, dimension_keywords):
    st.subheader(title)

    measures = numeric_columns(df)
    dimensions = dimension_columns(df)

    if df.empty:
        st.info("No records are available.")
        return

    if not measures:
        st.dataframe(df, use_container_width=True)
        return

    default_metric = preferred_column(measures, metric_keywords)

    # Exclude numeric identifiers from preferred measures.
    business_measures = [
        col
        for col in measures
        if not col.lower().endswith("_id")
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
                index=dimensions.index(default_dimension),
                key=f"{title}_dimension",
            )
        else:
            dimension = None

    if dimension:
        chart_data = (
            df.groupby(dimension, dropna=False)[metric]
            .sum()
            .sort_values(ascending=False)
            .head(15)
        )

        st.bar_chart(chart_data, horizontal=True)
    else:
        st.metric(
            "Total",
            f"{df[metric].sum():,.2f}",
        )

    with st.expander("View source data"):
        st.dataframe(df, use_container_width=True)


st.title("💊 PharmaFlow Analytics Dashboard")

st.caption(
    "Pharmacy Retail & Wholesale | "
    "Apache Airflow • AWS S3 • Bronze/Silver/Gold"
)

with st.sidebar:
    st.header("Data Source")

    st.write("AWS Region:", REGION)
    st.write("S3 Bucket:", BUCKET)

    if PROFILE:
        st.write("Authentication:", f"AWS Profile ({PROFILE})")
    else:
        st.write("Authentication:", "AWS Default Credential Chain")

    if st.button("Refresh data"):
        load_gold_data.clear()
        st.rerun()


try:
    datasets = load_gold_data(
        BUCKET,
        REGION,
        PROFILE,
    )

except (
    BotoCoreError,
    ClientError,
    ProfileNotFound,
    NoCredentialsError,
    OSError,
    ValueError,
    ImportError,
) as error:
    st.error("Unable to load Gold-layer datasets from AWS S3.")
    st.code(str(error))

    st.info(
        "Check AWS credentials or the EC2 IAM role, "
        "S3 permissions, bucket name, and Gold dataset paths. "
        "For local AWS SSO authentication, run "
        "'aws sso login --profile pharmaflow-dev'."
    )

    st.stop()


branches = datasets["Branches"]
medicines = datasets["Medicines"]
suppliers = datasets["Suppliers"]

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

st.divider()

st.caption(
    "PharmaFlow Data Engineering Platform | "
    "Synthetic pharmacy data for portfolio demonstration"
)
