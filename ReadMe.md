-----
# TP1 Report: Static Analysis & SecDevOps

**Authors:** Romain Billy, Amir Djelidi

-----

## 1\. Introduction and Access

The objective to this TP was to automate the detection of vulnerabilities in source code (SAST), dependencies (SCA), and exposed secrets using a CI pipeline.

## 2\. Project Description and Environment

### The Project

The analyzed application is a simple Web API built with **Flask** (Python). It was intentionally designed with common security vulnerabilities (OWASP Top 10) and configuration errors to demonstrate the effectiveness of automated security tools.

### Technical Environment

  * **Language:** Python 3.9
  * **Framework:** Flask (v1.1.2) and Werkzeug (v1.0.1) - *Outdated versions chosen for testing purposes.*
  * **Dependencies:** Defined in `requirements.txt`.
  * **CI Infrastructure:** GitHub Actions (Ubuntu Latest runner).

-----

## 3\. Actions Performed (CI Pipeline)

We implemented a Continuous Integration (CI) pipeline defined in `.github/workflows/security.yml`. This workflow triggers automatically on every `push` and `pull_request` targeting the `main` branch. If it fails, **the push/merge will be rejected** by github.

The pipeline orchestrates three distinct security scanning jobs:

1.  **SAST (Static Application Security Testing) with Semgrep:**

      * **Goal:** Analyze the `app.py` source code to detect insecure coding patterns.
      * **Configuration:** Used the `auto` config to detect standard Python vulnerabilities (SQL injection, XSS).

2.  **SCA (Software Composition Analysis) with Trivy:**

      * **Goal:** Scan the filesystem and `requirements.txt` to identify outdated libraries with known CVEs.
      * **Configuration:** Focused on `CRITICAL` and `HIGH` severity vulnerabilities.

3.  **Secret Scanning with Gitleaks:**

      * **Goal:** Scan the Git history and current files to detect hardcoded API keys or passwords.
      * **Configuration:** Set to export results in SARIF format for analysis.

-----

## 4\. Results and Findings

The following results were generated automatically by the CI pipeline and retrieved as build artifacts.

### Summary of Findings

| Analysis Type | Tool | Summary of Results | Max Severity |
| :--- | :--- | :--- | :--- |
| **SCA (Dependencies)** | Trivy | 3 Vulnerabilities (Flask & Werkzeug) | **HIGH** |
| **SAST (Code)** | Semgrep | 8 Alerts (SQL Injection, XSS, Debug Mode) | **ERROR** |
| **Secrets** | Gitleaks | 1 Secret detected (Generic API Key) | **CRITICAL** |

### A. SCA Analysis (Dependencies) - Trivy

The analysis of `requirements.txt` revealed the use of outdated Python libraries containing public vulnerabilities (CVEs).

**Detailed Findings:**

  * **Flask 1.1.2:** Vulnerable to **CVE-2023-30861** (Severity: High). This involves a possible disclosure of permanent session cookies due to a missing `Vary: Cookie` header.
  * **Werkzeug 1.0.1:**
      * **CVE-2023-25577** (Severity: High): Risk of Denial of Service (DoS) via high resource usage when parsing multipart form data.
      * **CVE-2024-34069** (Severity: High): Risk of arbitrary code execution via the debugger.

<img width="1730" height="627" alt="image" src="https://github.com/user-attachments/assets/8632c998-a7c5-4e8c-a093-20583530ce6b" />


### B. SAST Analysis (Source Code) - Semgrep

Semgrep scanned `app.py` and identified several critical logic vulnerabilities.

**Detailed Findings:**

1.  **SQL Injection (Lines 34 & 40):**

      * The code constructs a SQL query by directly concatenating user inputs (`username` and `password`).
      * **Rule Triggered:** `python.django.security.injection.tainted-sql-string` and `sqlalchemy-execute-raw-query`.
      * *Remediation:* Use parameterized queries/prepared statements.
      * <img width="905" height="329" alt="image" src="https://github.com/user-attachments/assets/131f35cc-483e-4baa-8ff7-be9eed7608b6" />


2.  **Cross-Site Scripting (XSS) / Template Injection (Lines 59-63):**

      * The use of `render_template_string` with an unescaped f-string (`f'''...{name}...'''`) allows for arbitrary code injection.
      * **Rule Triggered:** `python.flask.security.dangerous-template-string`.
      * <img width="445" height="166" alt="image" src="https://github.com/user-attachments/assets/afd3af5c-7e15-4882-bbb1-dd04ed61277d" />


3.  **Security Misconfiguration (Line 69):**

      * The application runs with `app.run(debug=True)`. In production, this leaks sensitive information and provides an interactive console on crash.
      * **Rule Triggered:** `python.flask.security.audit.debug-enabled`.
      * <img width="407" height="91" alt="image" src="https://github.com/user-attachments/assets/4956d2c8-04d8-48df-bfa4-5a3954196445" />

  

### C. Secret Scanning - Gitleaks

Gitleaks analyzed the codebase and detected a hardcoded secret that should not have been committed.

**Detailed Findings:**

  * **File:** `app.py` (Line 9)
  * **Rule ID:** `generic-api-key`
  * **Commit:** `09f4718...` by Romain Billy.
  * **Snippet:** The scan identified a variable pattern resembling an API Key (Redacted in the SARIF report).
  * <img width="619" height="22" alt="image" src="https://github.com/user-attachments/assets/8fed2fe4-721a-4559-81b2-1eca450339b9" />

-----

## 6\. Appendices

### Workflow Configuration ([.github/workflows/security.yml](.github/workflows/security.yml))


-----
