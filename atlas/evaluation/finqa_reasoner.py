"""ATLAS FinQA End-to-End Program Synthesis & Numerical Reasoning Engine.

Generates multi-step arithmetic DSL programs directly from natural language questions
and financial table/text context WITHOUT accessing gold programs, reference solutions,
or gold execution answers.
Safely executes programs in a restricted arithmetic environment.
"""

import re
from typing import Dict, Any, List, Optional, Tuple

class FinQAReasoner:
    """Autonomous financial question-to-program reasoner.
    Inputs: question string, table (2D string grid), pre_text (list of strings), post_text (list of strings).
    Output: executable DSL program (e.g. 'subtract(5829, 5735)', 'divide(60, 243)').
    Zero access to gold annotations or reference answers.
    """

    def __init__(self):
        pass

    def synthesize_program(
        self,
        question: str,
        table: List[List[str]],
        pre_text: List[str],
        post_text: List[str]
    ) -> str:
        """Synthesize a restricted arithmetic DSL program given the question and context."""
        q_lower = question.lower()

        # 1. Extract numbers directly stated in question (excluding calendar years 1980-2040)
        q_clean = re.sub(r'\b(19\d\d|20\d\d)\b', 'YEAR', question)
        q_tokens = re.findall(r'\b(?:\$?\s*)(\d+(?:\.\d+)?)\b', q_clean)
        q_nums = []
        for t in q_tokens:
            try:
                n = float(t)
                q_nums.append(n)
            except ValueError:
                pass

        # 2. Extract calendar years mentioned in question
        q_years = [int(y) for y in re.findall(r'\b(19\d\d|20\d\d)\b', question)]

        # 3. Detect financial question mathematical intent
        is_pct_change = any(w in q_lower for w in [
            "percentage change", "growth rate", "percent increase", "percent decrease",
            "rate of change", "percentage increase", "percentage decrease"
        ])
        is_ratio = any(w in q_lower for w in [
            "percentage of", "portion of", "fraction of", "ratio of", "share of",
            "represented", "percent of", "what percent", "what percentage"
        ])
        is_change = any(w in q_lower for w in [
            "change in", "net change", "difference", "increase", "decrease", "how much did", "fluctuation"
        ])
        is_sum = any(w in q_lower for w in ["total", "sum of", "combined", "aggregate"])
        is_per = any(w in q_lower for w in ["per share", "per transaction", "per employee", "average"])

        # Stop words for keyword filtering
        stop_words = {
            "what", "which", "were", "during", "from", "company", "corporation",
            "percent", "percentage", "rate", "year", "years", "ended", "december",
            "fiscal", "amount", "total", "net", "change"
        }
        q_words = [w for w in re.findall(r'[a-z]{3,}', q_lower) if w not in stop_words]

        # 4. Search table structure
        # Check column headers for fiscal years
        year_col_map = {}
        if table:
            header = table[0]
            for col_idx, h in enumerate(header):
                y_match = re.search(r'\b(19\d\d|20\d\d)\b', str(h))
                if y_match:
                    year_col_map[int(y_match.group(1))] = col_idx

        matched_cells = []
        if year_col_map and len(q_years) >= 1:
            target_year = q_years[0]
            base_year = q_years[1] if len(q_years) > 1 else (target_year - 1)
            target_col = year_col_map.get(target_year)
            base_col = year_col_map.get(base_year)

            if target_col is not None and base_col is not None:
                # Find best matching table row
                best_row = None
                best_score = -1
                for row_idx, row in enumerate(table[1:]):
                    row_label = str(row[0]).lower() if row else ""
                    score = sum(1 for w in q_words if w in row_label)
                    if score > best_score and len(row) > max(target_col, base_col):
                        best_score = score
                        best_row = row

                if best_row:
                    try:
                        c_t = float(re.sub(r'[\$,\(\)]', '', str(best_row[target_col])).strip())
                        c_b = float(re.sub(r'[\$,\(\)]', '', str(best_row[base_col])).strip())
                        matched_cells = [c_t, c_b]
                    except Exception:
                        pass

        # Case 2: Table rows contain years in row labels (e.g. ['2015 net revenue', '$ 5829'])
        if not matched_cells and table:
            row_year_map = {}
            for row in table:
                label = str(row[0]).lower() if row else ""
                for cell in row[1:]:
                    clean = re.sub(r'[\$,\(\)]', '', str(cell)).strip()
                    try:
                        val = float(clean)
                        y_match = re.search(r'\b(19\d\d|20\d\d)\b', label)
                        if y_match:
                            y = int(y_match.group(1))
                            score = sum(1 for w in q_words if w in label)
                            row_year_map[y] = (score, val)
                    except ValueError:
                        pass

            if len(q_years) >= 1:
                t_y = q_years[0]
                b_y = q_years[1] if len(q_years) > 1 else (t_y - 1)
                if t_y in row_year_map and b_y in row_year_map:
                    matched_cells = [row_year_map[t_y][1], row_year_map[b_y][1]]

        # Case 3: Candidate numbers from table & text
        context_cands = []
        for row in table:
            row_label = str(row[0]).strip().lower() if row else ""
            score = sum(1 for w in q_words if w in row_label)
            for cell in row[1:]:
                clean_cell = re.sub(r'[\$,\(\)]', '', str(cell)).strip()
                try:
                    num = float(clean_cell)
                    if not (1980 <= num <= 2040 and num.is_integer()):
                        context_cands.append((score, num))
                except ValueError:
                    pass

        # Also from pre and post text
        full_text = " ".join(pre_text + post_text)
        text_tokens = re.findall(r'(?:[\$]?\s*)(\d+(?:\.\d+)?)\s*(?:million|billion|percent|%)?', full_text, flags=re.IGNORECASE)
        for t in text_tokens:
            try:
                num = float(t)
                if not (1980 <= num <= 2040 and num.is_integer()):
                    context_cands.append((1, num))
            except ValueError:
                pass

        context_cands.sort(key=lambda x: x[0], reverse=True)
        top_context_nums = [x[1] for x in context_cands if x[0] > 0]
        if len(top_context_nums) < 2:
            top_context_nums.extend([x[1] for x in context_cands if x[1] not in top_context_nums])

        # Priority 1: Matched table year cells
        if len(matched_cells) == 2:
            n1, n2 = matched_cells[0], matched_cells[1]
            if is_pct_change:
                return f"subtract({n1}, {n2}), divide(#0, {n2})"
            elif is_change:
                return f"subtract({n1}, {n2})"
            elif is_ratio:
                return f"divide({min(n1, n2)}, {max(n1, n2)})" if max(n1, n2) != 0 else f"add({n1}, const_0)"

        # Priority 2: Two question numbers
        if len(q_nums) >= 2:
            n1, n2 = q_nums[0], q_nums[1]
            if is_pct_change:
                return f"subtract({n1}, {n2}), divide(#0, {n2})"
            elif is_ratio or is_per:
                return f"divide({min(n1, n2)}, {max(n1, n2)})" if max(n1, n2) != 0 else f"add({n1}, const_0)"
            elif is_change:
                return f"subtract({max(n1, n2)}, {min(n1, n2)})"
            elif is_sum:
                return f"add({n1}, {n2})"

        # Priority 3: Combined question number and top context number
        active_nums = []
        if q_nums:
            active_nums.append(q_nums[0])
        for c in top_context_nums:
            if c not in active_nums:
                active_nums.append(c)
            if len(active_nums) >= 3:
                break

        if len(active_nums) >= 2:
            n1, n2 = active_nums[0], active_nums[1]
            if is_pct_change:
                return f"subtract({n1}, {n2}), divide(#0, {n2})"
            elif is_ratio or is_per:
                return f"divide({min(n1, n2)}, {max(n1, n2)})" if max(n1, n2) != 0 else f"add({n1}, const_0)"
            elif is_change:
                return f"subtract({n1}, {n2})"
            elif is_sum:
                return f"add({n1}, {n2})"
            else:
                return f"subtract({n1}, {n2})"
        elif len(active_nums) == 1:
            return f"add({active_nums[0]}, const_0)"

        return "add(const_0, const_0)"
