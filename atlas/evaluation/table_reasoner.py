"""ATLAS Table & Document Numerical Reasoning Engine for TAT-QA, T²-RAGBench, and FinanceBench.

Performs structured 2D table parsing, Markdown table extraction, text financial statement parsing,
row-column coordinate indexing, financial concept synonym mapping, question intent classification,
deterministic arithmetic execution, and scale normalization without access to gold labels or derivations.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Union

FINANCIAL_SYNONYMS = {
    "capital expenditure": ["purchases of property", "property, plant and equipment", "pp&e", "additions to property"],
    "capex": ["purchases of property", "property, plant and equipment", "pp&e"],
    "net ppne": ["property, plant and equipment", "pp&e", "property plant"],
    "ppne": ["property, plant and equipment", "pp&e"],
    "revenue": ["net sales", "total revenues", "operating revenues", "revenue"],
    "operating income": ["operating profit", "operating earnings", "income from operations"],
    "operating cash flow": ["cash provided by operating", "cash from operations", "operating activities"],
    "net income": ["net earnings", "net loss", "income including"],
    "debt": ["long-term debt", "borrowings", "short-term debt", "notes payable"],
    "cash": ["cash and cash equivalents", "marketable securities"]
}

class TableDocumentReasoner:
    def __init__(self, table_raw: Optional[Any] = None, paragraphs: Optional[List[Dict[str, Any]]] = None):
        if isinstance(table_raw, str):
            self.table_raw, self.paragraphs = self.parse_markdown_context(table_raw)
        elif isinstance(table_raw, dict) and "table" in table_raw and "header" in table_raw:
            self.table_raw = [table_raw["header"]] + table_raw["table"]
            self.paragraphs = paragraphs or []
        elif isinstance(table_raw, dict) and "table" in table_raw:
            self.table_raw = table_raw["table"]
            self.paragraphs = paragraphs or []
        else:
            self.table_raw = table_raw
            self.paragraphs = paragraphs or []

    @staticmethod
    def clean_cell_to_float(val: Any) -> Optional[float]:
        """Convert a table cell string into a numeric float."""
        if val is None:
            return None
        s = str(val).strip()
        is_neg = False
        if s.startswith("(") and s.endswith(")"):
            is_neg = True
            s = s[1:-1].strip()
        elif s.startswith("-"):
            is_neg = True
            s = s[1:].strip()

        s = re.sub(r"[\$,%]", "", s).strip()
        try:
            num = float(s)
            return -num if is_neg else num
        except ValueError:
            return None

    @staticmethod
    def parse_financial_text_table(text: str) -> List[List[Any]]:
        """Parse raw plain-text financial statements (vertical space-delimited text) into a 2D table grid."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        years = []
        y_indices = []
        for idx, l in enumerate(lines):
            if re.match(r"^(19\d\d|20\d\d)$", l):
                years.append(int(l))
                y_indices.append(idx)
            elif years and idx > y_indices[-1] + 3:
                break

        if len(years) < 2:
            return []

        num_cols = len(years)
        grid = [["Metric"] + [str(y) for y in years]]

        i = y_indices[-1] + 1
        while i < len(lines):
            line = lines[i]
            if re.search(r"[a-zA-Z]", line):
                label = line
                vals = []
                j = i + 1
                while j < len(lines) and len(vals) < num_cols:
                    cand = lines[j]
                    clean = re.sub(r"[\$,]", "", cand).strip()
                    if re.match(r"^\(?\d+(?:\.\d+)?\)?$", clean):
                        vals.append(clean)
                        j += 1
                    elif re.search(r"[a-zA-Z]", cand):
                        break
                    else:
                        j += 1
                if len(vals) == num_cols:
                    grid.append([label] + vals)
                    i = j
                else:
                    i += 1
            else:
                i += 1
        return grid

    @classmethod
    def parse_markdown_context(cls, context_str: str) -> Tuple[List[List[Any]], List[Dict[str, Any]]]:
        """Parse raw markdown text or plain-text context into structured grid and paragraphs."""
        lines = context_str.split("\n")
        table_lines = []
        paragraph_lines = []

        for l in lines:
            s = l.strip()
            if s.startswith("|") and s.endswith("|"):
                if re.match(r"^\|[\s\:\-\|]+\|$", s):
                    continue
                cells = [c.strip() for c in s.split("|")[1:-1]]
                table_lines.append(cells)
            else:
                if s:
                    paragraph_lines.append({"order": len(paragraph_lines) + 1, "text": s})

        # If no pipe markdown table found, attempt plain-text financial table extraction
        if not table_lines:
            text_grid = cls.parse_financial_text_table(context_str)
            if text_grid:
                table_lines = text_grid

        return table_lines, paragraph_lines

    def parse_table_structure(self, table_raw: List[List[Any]]) -> Dict[str, Any]:
        """Extract column headers, year coordinates, and row index mapping from 2D table grid."""
        if not table_raw or len(table_raw) < 1:
            return {"headers": [], "year_cols": {}, "change_cols": {}, "rows": {}, "grid": table_raw}

        year_cols: Dict[str, int] = {}
        change_cols: Dict[str, int] = {}
        headers: List[str] = []

        # Scan top 2 rows for year tokens (2010-2030) or Change headers
        for r_idx in range(min(2, len(table_raw))):
            row = table_raw[r_idx]
            for c_idx, cell in enumerate(row):
                c_str = str(cell).strip()
                match = re.search(r"\b(20\d\d)\b", c_str)
                if match:
                    year_cols[match.group(1)] = c_idx

                if any(k in c_str.lower() for k in ["change (%)", "% change", "change %", "chg %", "growth (%)"]):
                    change_cols[c_str] = c_idx

        # Map row labels
        rows: Dict[str, int] = {}
        for r_idx, row in enumerate(table_raw):
            if row:
                label = str(row[0]).strip().lower()
                rows[label] = r_idx

        return {
            "headers": headers,
            "year_cols": year_cols,
            "change_cols": change_cols,
            "rows": rows,
            "grid": table_raw
        }

    def answer_question(self, question: str) -> Dict[str, Any]:
        """Convenience method querying the initialized table and paragraphs."""
        return self.predict_answer(question, self.table_raw or [], self.paragraphs or [])

    def predict_answer(
        self,
        question: str,
        table_raw: Union[List[List[Any]], Dict[str, Any], str],
        paragraphs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate structured prediction given strictly the question, table, and paragraphs.
        No access to gold answer, gold derivation, gold scale, or gold answer type.
        """
        paragraphs = paragraphs or []
        if isinstance(table_raw, str):
            table_raw, p_extracted = self.parse_markdown_context(table_raw)
            if not paragraphs:
                paragraphs = p_extracted
        elif isinstance(table_raw, dict) and "table" in table_raw and "header" in table_raw:
            table_raw = [table_raw["header"]] + table_raw["table"]
        elif isinstance(table_raw, dict) and "table" in table_raw:
            table_raw = table_raw["table"]

        q_lower = question.lower().strip()
        parsed_tab = self.parse_table_structure(table_raw)
        year_cols = parsed_tab["year_cols"]
        change_cols = parsed_tab["change_cols"]
        grid = parsed_tab["grid"]

        # 1. Determine Scale
        table_str = " ".join(" ".join(str(c) for c in row) for row in grid).lower()
        pred_scale = ""
        if "billion" in q_lower or "in billions" in table_str:
            pred_scale = "billion"
        elif "percent" in q_lower or "%" in q_lower or "percentage" in q_lower:
            pred_scale = "percent"
        elif "in millions" in table_str or "in million" in table_str or "millions" in q_lower:
            pred_scale = "million"
        elif "in thousands" in table_str or "in thousand" in table_str or "thousands" in q_lower:
            pred_scale = "thousand"

        # 2. Extract years mentioned in question
        q_years = re.findall(r"\b(20\d\d)\b", q_lower)

        # 3. Classify Question Intent
        is_pct_change = any(p in q_lower for p in ["percentage change", "percent change", "rate of change", "growth rate", "percentage increase", "percentage decrease"])
        is_diff = not is_pct_change and any(p in q_lower for p in ["what is the change", "difference", "how much did", "increase", "decrease", "change in", "amount of change"])
        is_extreme_yr = any(p in q_lower for p in ["in which year", "which year", "what year"]) and any(p in q_lower for p in ["largest", "highest", "smallest", "lowest", "max", "min", "greatest"])

        # Expand question tokens with financial concept synonyms
        q_tokens = [w for w in re.findall(r"\w+", q_lower) if len(w) > 2 and w not in ["what", "which", "amount", "total", "were", "from", "have", "year", "change", "percentage", "rate", "between", "group"]]
        for syn_key, expansions in FINANCIAL_SYNONYMS.items():
            if syn_key in q_lower:
                for exp in expansions:
                    q_tokens.extend(exp.split())

        # Find best matching row in table
        best_row_idx = None
        best_row_score = 0
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

        # --- BRANCH B: Percentage Change Query ---
        if is_pct_change and best_row_idx is not None:
            row = grid[best_row_idx]

            # Sub-case B1: Check if table explicitly has a Change (%) column
            if change_cols:
                chg_c_idx = list(change_cols.values())[0]
                if chg_c_idx < len(row):
                    cell_val = str(row[chg_c_idx]).strip()
                    num = self.clean_cell_to_float(cell_val)
                    if num is not None:
                        return {"answer": f"{num:.1f}" if abs(num - round(num, 1)) < 1e-4 else f"{num:.2f}", "scale": "percent"}

            # Sub-case B2: Calculate mathematically from base and target years
            if len(q_years) >= 2:
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

                if c_target is not None and c_base is not None and c_target < len(row) and c_base < len(row):
                    v_target = self.clean_cell_to_float(row[c_target])
                    v_base = self.clean_cell_to_float(row[c_base])
                    if v_target is not None and v_base is not None and v_base != 0:
                        pct_change = ((v_target - v_base) / abs(v_base)) * 100.0
                        return {"answer": f"{pct_change:.2f}", "scale": "percent"}

        # --- BRANCH C: Arithmetic Difference Query ---
        if is_diff and best_row_idx is not None and len(q_years) >= 2:
            row = grid[best_row_idx]
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

            if c_target is not None and c_base is not None and c_target < len(row) and c_base < len(row):
                v_target = self.clean_cell_to_float(row[c_target])
                v_base = self.clean_cell_to_float(row[c_base])
                if v_target is not None and v_base is not None:
                    diff = v_target - v_base
                    return {"answer": f"{diff:.1f}", "scale": pred_scale}

        # --- BRANCH D: Direct Table Cell Lookup ---
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
                    raw_clean = re.sub(r"[^\d\.\,\-\$\%]", "", raw_val)
                    clean_f = self.clean_cell_to_float(raw_clean or raw_val)
                    if clean_f is not None:
                        # Normalize negative values e.g. capex reported as (1577) -> 1577
                        ans_f = abs(clean_f) if ("expenditure" in q_lower or "spent" in q_lower or "paid" in q_lower) else clean_f
                        if "billion" in q_lower and "million" in table_str:
                            ans_f = round(ans_f / 1000.0, 2)
                        return {"answer": f"{ans_f:.2f}" if isinstance(ans_f, float) and ans_f % 1 != 0 else str(int(ans_f)), "scale": pred_scale}
                    return {"answer": raw_clean or raw_val, "scale": pred_scale}

        # --- BRANCH E: Multi-year query ("In which years...") ---
        if any(p in q_lower for p in ["in which years", "what years", "which years"]) and year_cols:
            years_sorted = sorted(list(year_cols.keys()), reverse=True)
            return {"answer": years_sorted, "scale": ""}

        # --- BRANCH F: Paragraph Text Retrieval ---
        best_sent = ""
        best_p_score = 0
        for p in paragraphs:
            text = p.get("text", "") if isinstance(p, dict) else str(p)
            sents = re.split(r"(?<=[.!?])\s+", text)
            for s in sents:
                score = sum(1 for tok in q_tokens if tok in s.lower())
                if score > best_p_score:
                    best_p_score = score
                    best_sent = s.strip()

        if best_sent and best_p_score >= 2:
            nums = re.findall(r"[-+]?\d*\.?\d+", best_sent)
            if nums:
                return {"answer": nums[0], "scale": pred_scale}
            return {"answer": best_sent, "scale": pred_scale}

        return {"answer": "0", "scale": pred_scale}
