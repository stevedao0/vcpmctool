# vcpmctool/core/pipeline.py (Phiên bản cuối cùng)
import pandas as pd
from typing import List, Tuple
from .excel_io import read_input_excel, write_output_excel
from .processing_steps import row_processor, column_mapper
from services.file_utils import generate_output_name
from services.logger import Logger


def process_files(
        input_paths: List[str],
        initial_term: int,
        ext_term: int,
        # royalty_rate đã được loại bỏ
        logger: Logger,
        auto_backup: bool = True,
        auto_proper: bool = True
) -> Tuple[pd.DataFrame, bool]:
    all_outputs = []
    overall_success = True

    options = {
        "initial_term": initial_term,
        "ext_term": ext_term,
        "auto_proper": auto_proper
    }

    # ... (Phần còn lại của file giữ nguyên như phiên bản trước)
    for path in input_paths:
        try:
            df_input, read_success = read_input_excel(path)
            if not read_success:
                logger.error(f"Failed to read {path} - may be open. Skipping.")
                overall_success = False
                continue

            df_input.columns = [col.strip() for col in df_input.columns]
            output_rows = []
            prev_state = {}

            for idx, row in df_input.iterrows():
                try:
                    new_row, prev_state = row_processor.process_single_row(
                        row, prev_state, options)
                    output_rows.append(new_row)
                except Exception as row_e:
                    logger.warning(
                        f"Error processing row {idx} in {path}: {row_e}")
                    output_rows.append(
                        {"Error": str(row_e), "STT": row.get("STT", "")})

            df_output = pd.DataFrame(output_rows)

            processed_and_mapped_cols = set(column_mapper.OUTPUT_COLUMNS)
            input_cols_in_mapping = set()
            for cols in column_mapper.HEADER_MAPPING.values():
                input_cols_in_mapping.update(cols)

            extra_cols = [
                col for col in df_input.columns
                if col not in input_cols_in_mapping and col not in processed_and_mapped_cols
            ]

            if extra_cols:
                df_output = pd.concat(
                    [df_output, df_input[extra_cols].reset_index(drop=True)], axis=1)

            all_outputs.append(df_output)
            logger.info(f"Processed {path}")

        except Exception as e:
            logger.error(f"Unexpected error processing {path}: {e}")
            overall_success = False

    if not all_outputs:
        logger.error("No valid outputs generated.")
        return pd.DataFrame(), False

    final_df = pd.concat(all_outputs, ignore_index=True)

    final_ordered_cols = column_mapper.OUTPUT_COLUMNS
    extra_final_cols = [
        col for col in final_df.columns if col not in final_ordered_cols]

    final_df = final_df[final_ordered_cols + extra_final_cols]

    output_path = generate_output_name(input_paths[0], "_Ket_qua.xlsx")
    write_success = write_output_excel(final_df, output_path, auto_backup)

    if not write_success:
        logger.error("Write failed - check if output file is open.")
        overall_success = False
    else:
        logger.info(f"Output saved to {output_path}")

    return final_df, overall_success
