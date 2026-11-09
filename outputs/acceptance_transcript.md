# Acceptance Test Run Transcript (Cases A01 - A20)

| ID | Session | Question | Status | Intent | Conf | Route | Attempts | Answer Text |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| A01 | s1 | What was Pune's revenue on 15 May 2026? | Answered | lookup | 1.00 | python | 1 | Pune's revenue inr on 2026-05-15 was INR 623845.00. |
| A02 | s1 | And the target? | Answered | lookup | 1.00 | python | 1 | Pune's daily target inr on 2026-05-15 was INR 900000.00. |
| A03 | s1 | How about Mumbai? | Answered | lookup | 1.00 | python | 1 | Mumbai's daily target inr on 2026-05-15 was INR 1050000.00. |
| A04 | s2 | How is Hyderabad doing? | Clarification Needed | lookup | 0.40 | none | 0 | Could you please specify the metric and date? |
| A05 | s2 | revenue on 2026-05-15 | Answered | lookup | 1.00 | python | 1 | Hyderabad's revenue inr on 2026-05-15 was INR 786399.27. |
| A06 | s3 | What was Hydrabad's turnover yesterday? | Answered | lookup | 0.94 | python | 1 | Hyderabad's revenue inr on 2026-06-29 was INR 784954.90. |
| A07 | s4 | Did Pune hit its target on 2026-05-16? | Drafted | target_vs_actual | 1.00 | python | 1 | Pune on 2026-05-16 did not hit its target (achievement 74.59%, band Poor), posting revenue of INR 671332.65 against target INR 900000.00. |
| A08 | s4 | Did Pune hit its target on 2026-05-20? | Answered | target_vs_actual | 1.00 | python | 1 | Pune on 2026-05-20 hit its target with achievement 75.30% (band Good), posting revenue of INR 677739.77 against target INR 900000.00. |
| A09 | s4 | Did Mumbai hit its target on 2026-05-21? | Answered | target_vs_actual | 1.00 | python | 1 | Mumbai on 2026-05-21 hit its target with achievement 107.99% (band Excellent), posting revenue of INR 1133910.49 against target INR 1050000.00. |
| A10 | s5 | Which store had the highest average revenue between 2026-05-01 and 2026-05-31? | Answered | comparison | 1.00 | sql | 1 | Mumbai INR 1071614.03; Bengaluru INR 916766.02; Hyderabad INR 900317.89; Ahmedabad INR 798849.31; Pune INR 643251.34; highest Mumbai |
| A11 | s5 | Which store had the lowest revenue on 2026-06-10? | Answered | comparison | 1.00 | sql | 1 | Pune INR 602942.85; Hyderabad INR 807522.21; Ahmedabad INR 819290.32; Bengaluru INR 848248.05; Mumbai INR 903822.34 |
| A12 | s6 | Which stores are below the reorder threshold for Amul Milk? | Answered | inventory | 1.00 | sql | 1 | Stores short of stock for Amul Milk 1L: Hyderabad 40 units and Pune 85 units against threshold 100. |
| A13 | s6 | What are customers saying about Hyderabad? | Answered | feedback | 1.00 | sql | 1 | Customer feedback for Hyderabad: average rating 2.63, 38 rated of 40, most frequent theme Stock availability. |
| A14 | s7 | What was Pune's profit margin on 2026-05-15? | Safe Failure | unsupported_metric | 1.00 | none | 0 | The requested field is not an approved metric. Please ask for approved metrics such as revenue, footfall, target, stockout hours, or discount percentage. |
| A15 | s8 | What is the capital of India? | Escalated | out_of_scope | 1.00 | none | 0 | This request is outside the operational scope of DMart analytics or requests an unsupported action. Escalating to human management. |
| A16 | s9 | What was Mumbai's revenue on 2026-07-15? | Safe Failure | lookup | 1.00 | none | 0 | The requested date is out of range. Data is only available between 2026-04-01 and 2026-06-29. |
| A17 | s10 | Why is Pune's revenue so low? | Escalated | diagnostic | 1.00 | none | 0 | Diagnostic and root-cause inquiries require qualitative review. An analyst is needed to review store performance. |
| A18 | s11 | What was Kolkata's revenue on 2026-05-15? | Clarification Needed | lookup | 0.40 | none | 0 | Which store are you referring to? Please specify one of the five regional stores: Mumbai, Pune, Hyderabad, Bengaluru, or Ahmedabad. |
| A19 | s12 | What was Pune's revenue on 15 May 2026? | Answered | lookup | 1.00 | python | 3 | Pune's revenue inr on 2026-05-15 was INR 623845.00. |
| A20 | s13 | What was Pune's revenue on 15 May 2026? | Escalated | lookup | 1.00 | python | 3 | Data service unavailable after three attempts. Query escalated to technical support. |
