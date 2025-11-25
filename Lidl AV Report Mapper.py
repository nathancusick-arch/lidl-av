import streamlit as st
import pandas as pd
import datetime as dt
import io

st.title("Lidl AV Report Mapper")

st.write("""
          1. Export Lidl AV Alcohol - No ID data for the entire current round
          2. Drop the file in the below box, it should then give you the output file in your downloads
          3. Use following formulae to pull data through to the Lidl report:
            \n=XLOOKUP($A4&"-"&RIGHT(D$3, 1), 'Lidl AV Raw Data.csv'!$W:$W, 'Lidl AV Raw Data.csv'!$O:$O)
            \n=UPPER(XLOOKUP($A4&"-"&RIGHT(D$3, 1), 'Lidl AV Raw Data.csv'!$W:$W, 'Lidl AV Raw Data.csv'!$AJ:$AJ))
          4. Copy and paste over values etc!!!
          5. Done.
          """)

uploaded = st.file_uploader("Upload audits_basic_data_export.csv", type=["csv"])

if uploaded:

    # ------------------------------------------------------------
    # 1. Load input (unchanged, except uses uploaded file)
    # ------------------------------------------------------------
    df = pd.read_csv(uploaded, encoding="utf-8")

    # ------------------------------------------------------------
    # 2. Parse date and time with correct formats (unchanged)
    # ------------------------------------------------------------

    # Strict DD/MM/YYYY
    df["date_of_visit"] = pd.to_datetime(
        df["date_of_visit"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    # Parse time → HH:MM
    def parse_time_to_str(t):
        if pd.isna(t):
            return ""
        t = str(t).strip()

        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return dt.datetime.strptime(t, fmt).strftime("%H:%M")
            except ValueError:
                continue
        return ""

    df["time_of_visit"] = df["time_of_visit"].apply(parse_time_to_str)

    # ------------------------------------------------------------
    # 3. Sort chronologically (unchanged)
    # ------------------------------------------------------------
    df = df.sort_values(
        by=["date_of_visit", "time_of_visit"],
        ascending=[True, True]
    )

    # ------------------------------------------------------------
    # 4. number_of_visits (unchanged)
    # ------------------------------------------------------------
    df["number_of_visits"] = df.groupby("site_code").cumcount() + 1

    # ------------------------------------------------------------
    # 5. site_code_visit_number (unchanged)
    # ------------------------------------------------------------
    df["site_code_visit_number"] = (
        '="' +
        df["site_code"].astype(str) +
        "-" +
        df["number_of_visits"].astype(str) +
        '"'
    )

    # ------------------------------------------------------------
    # 6. Reorder columns (unchanged)
    # ------------------------------------------------------------
    cols = list(df.columns)

    cols.remove("number_of_visits")
    cols.remove("site_code_visit_number")

    site_code_index = cols.index("site_code")

    cols.insert(site_code_index + 1, "number_of_visits")
    cols.insert(site_code_index + 2, "site_code_visit_number")

    df = df[cols]

    # ------------------------------------------------------------
    # 7. Output (Streamlit version)
    # ------------------------------------------------------------
    output_bytes = io.BytesIO()
    df.to_csv(output_bytes, index=False, encoding="utf-8-sig")
    output_bytes.seek(0)

    st.success("File processed successfully!")

    st.download_button(
        label="Download Lidl AV Raw Data CSV",
        data=output_bytes.getvalue(),
        file_name="Lidl AV Raw Data.csv",
        mime="text/csv"
    )
