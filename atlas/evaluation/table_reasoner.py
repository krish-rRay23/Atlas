"""ATLAS Table & Document Numerical Reasoning Engine for TAT-QA.

Performs structured 2D table parsing, row-column coordinate indexing,
question intent classification, deterministic arithmetic execution,
and scale normalization without access to gold labels or derivations.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Union

class TableDocumentReasoner:
    def __init__(self, table_raw: Optional[Any] = None, paragraphs: Optional[List[Dict[str, Any]]] = None):
        if isinstance(table_raw, dict) and "table" in table_raw and "header" in table_raw:
            self.table_raw = [table_raw["header"]] + table_raw["table"]
        elif isinstance(table_raw, dict) and "table" in table_raw:
            self.table_raw = table_raw["table"]
        else:
            self.table_raw = table_raw
        self.paragraphs = paragraphs or []

    def answer_question(self, question: str) -> Dict[str, Any]:
        """Convenience method to query the initialized table and paragraphs."""
        return self.predict_answer(question, self.table_raw or [], self.paragraphs or [])

    @staticmethod
    def clean_cell_to_float(val: Any) -> Optional[float]:
        """Convert a table cell string into a numeric float."""
        if val is None:
            return None
        s = str(val).strip()
        # Handle parenthesized negative numbers e.g. (12.4) -> -12.4
        is_neg = False
        if s.startswith("(") and s.endswith(")"):
            is_neg = True
            s = s[1:-1].strip()
        elif s.startswith("-"):
            is_neg = True
            s = s[1:].strip()

        # Remove currency symbols, commas, percent
        s = re.sub(r"[\$,%]", "", s).strip()
        try:
            num = float(s)
            return -num if is_neg else num
        except ValueError:
            return None

    def parse_table_structure(self, table_raw: List[List[Any]]) -> Dict[str, Any]:
        """Extract column headers, year coordinates, and row index mapping from 2D table grid."""
        if not table_raw or len(table_raw) < 2:
            return {"headers": [], "year_cols": {}, "rows": {}, "grid": table_raw}

        # Identify header rows (usually row 0 or 1 contains years / periods)
        year_cols: Dict[str, int] = {}
        headers: List[str] = []

        # Scan first 2 rows for year tokens (2010-2030)
        for r_idx in range(min(3, len(table_raw))):
            row = table_raw[r_idx]
            for c_idx, cell in enumerate(row):
                c_str = str(cell).strip()
                match = re.search(r"\b(20\d\d)\b", c_str)
                if match:
                    yr = match.group(1)
                    if yr not in year_cols:
                        year_cols[yr] = c_idx

        # If header has text column names
        if len(table_raw) > 1:
            headers = [str(c).strip() for c in table_raw[1]]

        # Map row label to row index
        rows: Dict[str, int] = {}
        for r_idx in range(len(table_raw)):
            row = table_raw[r_idx]
            if row and len(row) > 0:
                label = str(row[0]).strip().lower()
                if label:
                    rows[label] = r_idx

        return {
            "year_cols": year_cols,
            "headers": headers,
            "rows": rows,
            "grid": table_raw
        }

    def predict_answer(
        self,
        question: str,
        table_raw: Union[List[List[Any]], Dict[str, Any]],
        paragraphs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate structured prediction given strictly the question, table, and paragraphs.
        No access to gold answer, gold derivation, gold scale, or gold answer type.
        """
        if isinstance(table_raw, dict) and "table" in table_raw and "header" in table_raw:
            table_raw = [table_raw["header"]] + table_raw["table"]
        elif isinstance(table_raw, dict) and "table" in table_raw:
            table_raw = table_raw["table"]

        q_lower = question.lower().strip()
        parsed_tab = self.parse_table_structure(table_raw)
        year_cols = parsed_tab["year_cols"]
        grid = parsed_tab["grid"]

        # 1. Determine Scale
        table_str = " ".join(" ".join(str(c) for c in row) for row in grid).lower()
        pred_scale = ""
        if "percent" in q_lower or "%" in q_lower or "percentage" in q_lower:
            pred_scale = "percent"
        elif "in millions" in table_str or "in million" in table_str or "millions" in q_lower:
            pred_scale = "million"
        elif "in thousands" in table_str or "in thousand" in table_str or "thousands" in q_lower:
            pred_scale = "thousand"

        # 2. Extract years mentioned in question
        q_years = re.findall(r"\b(20\d\d)\b", q_lower)

        # 3. Classify Question Intent
        is_pct_change = any(p in q_lower for p in ["percentage change", "percent change", "rate of change", "growth rate"])
        is_diff = not is_pct_change and any(p in q_lower for p in ["what is the change", "difference", "how much did", "increase", "decrease", "change in"])
        is_extreme_yr = any(p in q_lower for p in ["in which year", "which year", "what year"]) and any(p in q_lower for p in ["largest", "highest", "smallest", "lowest", "max", "min", "greatest"])

        # Find best matching row in table
        best_row_idx = None
        best_row_score = 0
        q_tokens = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3 and w not in ["what", "which", "amount", "total", "were", "from", "have", "year", "change", "percentage"]]

        for r_idx, row in enumerate(grid):
            r_label = str(row[0]).lower() if row else ""
            score = sum(1 for tok in q_tokens if tok in r_label)
            if score > best_row_score:
                best_row_score = score
                best_row_idx = r_idx

        # If no specific row match, check if question targets "total"
        if best_row_idx is None and "total" in q_lower:
            for r_idx, row in enumerate(grid):
                r_label = str(row[0]).lower() if row else ""
                if "total" in r_label:
                    best_row_idx = r_idx
                    break

        # --- BRANCH A: Extreme Year Query ("In which year is X largest?") ---
        if is_extreme_yr and best_row_idx is not None and year_cols:
            row = grid[best_row_idx]
            find_max = any(w in q_lower for w in ["largest", "highest", "max", "greatest"])
            best_yr = None
            best_val = None

            for yr, c_idx in year_cols.items():
                if c_idx < len(row):
                    num = self.clean_cell_to_float(row[c_idx])
                    if num is not None:
                        if best_val is None:
                            best_val = num
                            best_yr = yr
                        elif find_max and num > best_val:
                            best_val = num
                            best_yr = yr
                        elif not find_max and num < best_val:
                            best_val = num
                            best_yr = yr

            if best_yr:
                return {"answer": str(best_yr), "scale": ""}

        # --- BRANCH B: Percentage Change Query ("What is the percentage change in X in Y1 from Y2?") ---
        if is_pct_change and best_row_idx is not None and len(q_years) >= 2:
            from_match = re.search(r"\bfrom\s+(20\d\d)\b", q_lower)
            to_match = re.search(r"\bto\s+(20\d\d)\b", q_lower)
            in_match = re.search(r"\bin\s+(20\d\d)\b", q_lower)

            if from_match and to_match:
                base_yr = from_match.group(1)
                target_yr = to_match.group(1)
            elif in_match and from_match:
                target_yr = in_match.group(1)
                base_yr = from_match.group(1)
            else:
                sorted_yrs = sorted([q_years[0], q_years[1]])
                base_yr, target_yr = sorted_yrs[0], sorted_yrs[1]

            c_target = year_cols.get(target_yr)
            c_base = year_cols.get(base_yr)
            row = grid[best_row_idx]

            if c_target is not None and c_base is not None and c_target < len(row) and c_base < len(row):
                v_target = self.clean_cell_to_float(row[c_target])
                v_base = self.clean_cell_to_float(row[c_base])
                if v_target is not None and v_base is not None and v_base != 0:
                    pct_change = ((v_target - v_base) / abs(v_base)) * 100.0
                    return {"answer": f"{pct_change:.2f}", "scale": "percent"}

        # --- BRANCH C: Arithmetic Difference Query ("What is the change in X in Y1 from Y2?") ---
        if is_diff and best_row_idx is not None and len(q_years) >= 2:
            from_match = re.search(r"\bfrom\s+(20\d\d)\b", q_lower)
            to_match = re.search(r"\bto\s+(20\d\d)\b", q_lower)
            in_match = re.search(r"\bin\s+(20\d\d)\b", q_lower)

            if from_match and to_match:
                base_yr = from_match.group(1)
                target_yr = to_match.group(1)
            elif in_match and from_match:
                target_yr = in_match.group(1)
                base_yr = from_match.group(1)
            else:
                sorted_yrs = sorted([q_years[0], q_years[1]])
                base_yr, target_yr = sorted_yrs[0], sorted_yrs[1]

            c_target = year_cols.get(target_yr)
            c_base = year_cols.get(base_yr)
            row = grid[best_row_idx]

            if c_target is not None and c_base is not None and c_target < len(row) and c_base < len(row):
                v_target = self.clean_cell_to_float(row[c_target])
                v_base = self.clean_cell_to_float(row[c_base])
                if v_target is not None and v_base is not None:
                    diff = v_target - v_base
                    return {"answer": f"{diff:.1f}", "scale": pred_scale}

        # --- BRANCH D: Direct Table Cell Lookup ("What is the amount of X in Y?") ---
        if best_row_idx is not None:
            row = grid[best_row_idx]
            target_col = None
            if q_years:
                target_col = year_cols.get(q_years[0])
            elif len(row) > 1:
                target_col = 1

            if target_col is not None and target_col < len(row):
                raw_val = str(row[target_col]).strip()
                if raw_val:
                    return {"answer": raw_val, "scale": pred_scale}

        # --- BRANCH E: Multi-year query ("In which years...") ---
        if any(p in q_lower for p in ["in which years", "what years", "which years"]) and year_cols:
            years_sorted = sorted(list(year_cols.keys()), reverse=True)
            return {"answer": years_sorted, "scale": ""}

        # --- BRANCH F: Multi-span / category query ("What are the types/categories of X in the table?") ---
        if any(p in q_lower for p in ["types of", "categories of", "what are the segments"]) and q_tokens:
            target_term = q_tokens[0] if q_tokens else ""
            matching_rows = []
            for row in grid:
                if row:
                    label = str(row[0]).strip()
                    if target_term in label.lower() and label not in matching_rows:
                        matching_rows.append(label)
            if len(matching_rows) >= 2:
                return {"answer": matching_rows, "scale": ""}

        # --- BRANCH G: Paragraph Text Retrieval ---
        # If question not resolved in table, search paragraph text for high token overlap
        best_sent = ""
        best_p_score = 0
        for p in paragraphs:
            text = p.get("text", "")
            sents = re.split(r"(?<=[.!?])\s+", text)
            for s in sents:
                score = sum(1 for tok in q_tokens if tok in s.lower())
                if score > best_p_score:
                    best_p_score = score
                    best_sent = s.strip()

        if best_sent and best_p_score >= 2:
            return {"answer": best_sent, "scale": pred_scale}

        return {"answer": "0", "scale": pred_scale}
